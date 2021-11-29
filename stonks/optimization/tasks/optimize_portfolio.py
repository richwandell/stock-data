import datetime
import hashlib
import json
import os
from typing import List, Tuple

import pandas as pd
from celery import shared_task
import numpy as np
from scipy import optimize
from .optimize import portfolio_volatility
from multiprocessing import Queue, Pool
from django.db import connection
import django
django.setup()


def pool_init(queue):
    global q

    q = queue


def efficient_return(all_inputs):
    returns_annual, cov_annual, order, target = all_inputs
    num_assets = len(returns_annual)
    args = (returns_annual, cov_annual)

    def portfolio_return(weights):
        return np.dot(weights, returns_annual)

    constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for asset in range(num_assets))
    result = optimize.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP',
                               bounds=bounds, constraints=constraints)
    q.put((order, result))


def compute_portfolio(all_inputs):
    # populate the empty lists with each portfolios returns,risk and weights
    risk_free_asset_return, to_compute, num_assets, av_returns, cov = all_inputs
    return_vals = []
    for _ in range(to_compute):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, av_returns)

        risk = np.sqrt(np.dot(weights.T, np.dot(weights, cov)))
        sharpe = (returns - risk_free_asset_return) / risk
        return_vals.append((weights, risk, returns, sharpe))

    q.put(tuple(return_vals))


class PortfolioOptimizer:
    SELECT_SYMBOLS_WITH_THIS_MONTH_AND_FIVE_YEARS = """
        select
            distinct sp.symbol
        from
             stonksconfig_symbolprice sp
        where
            sp.symbol in (
                select distinct symbol
                from stonksconfig_symbolprice spp
                where
                  spp.symbol in (%(symbols)s) 
                  and spp.date_time >= date_trunc('month', current_date - INTERVAL '5 year')
                  and spp.date_time < date_trunc('month', current_date - INTERVAL '5 year' + INTERVAL '1 month')
            )
            and sp.date_time >= date_trunc('month', current_date);
    """

    SELECT_MONTHLY_SYMBOLS_AS_DATAFRAME = """
    select
         concat(date_part('year', sp.date_time)::text,
             '-',
             lpad(date_part('month', sp.date_time)::text, 2, '0')
         ) as date_time,
         sp.symbol,
         sp.adjusted_close
    from stonksconfig_symbolprice sp
    where sp.symbol in (%(symbols)s)
    and sp.date_time in (%(dates)s)
    order by symbol asc , date_time asc;
    """

    def __init__(self):
        self.queue = Queue()
        self.pool = Pool(initializer=pool_init, initargs=(self.queue,), processes=os.cpu_count())

    def get_monthly_portfolio_stats(self, portfolio: List[str]) -> Tuple[np.ndarray, np.ndarray, list]:
        self.__load_symbols(portfolio)
        df = self.get_monthly_symbols_as_dataframe(portfolio)
        df['date_time'] = pd.to_datetime(df['date_time'])
        df = df.set_index('date_time')
        df = df.pivot(columns='symbol')
        df = df.fillna(method='ffill')
        df = df.fillna(method='bfill')
        column_names = [x[1] for x in list(df)]

        returns_monthly = df.pct_change()
        returns_monthly = returns_monthly.replace([np.inf], 1.0)
        returns_mean = returns_monthly.mean().to_numpy()
        annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
        std = returns_monthly.std().to_numpy() * np.sqrt(12.0)
        return std, annualized_return, column_names

    def __load_symbols(self, symbols):
        from ...stonksconfig.tasks.load_alphavantage_prices import AlphaVantage
        from ...stonksconfig.models import DataSourceCredential, DataSource

        sources_creds = DataSourceCredential.objects.select_related('user') \
            .filter(datasource__dstype__in=[DataSource.Sources.ALPHAVANTAGE]).first()

        av = AlphaVantage(sources_creds)
        av.load_symbols(symbols)

    def get_first_day_of_month_for_past_x_years(self, years: int):
        now = datetime.datetime.now()
        first_days = []
        first_of_month = datetime.datetime(year=now.year, month=now.month, day=1)
        target_month = datetime.datetime(year=now.year-years, month=now.month, day=1)
        while first_of_month >= target_month:
            first_days.append(f"{first_of_month.year}-{first_of_month.month if first_of_month.month >= 10 else '0'+str(first_of_month.month)}-01")
            if first_of_month.month == 1:
                first_of_month = datetime.datetime(year=first_of_month.year-1, month=12, day=1)
            else:
                first_of_month = datetime.datetime(year=first_of_month.year, month=first_of_month.month-1, day=1)
        return first_days

    def get_monthly_symbols_as_dataframe(self, portfolio: List[str]):
        query = self.SELECT_SYMBOLS_WITH_THIS_MONTH_AND_FIVE_YEARS % {"symbols": "'" + "','".join(portfolio) + "'"}
        with connection.cursor() as cursor:
            cursor.execute(query)
            items = list([x[0] for x in cursor.fetchall()])
        days_of_month = self.get_first_day_of_month_for_past_x_years(5)
        query = self.SELECT_MONTHLY_SYMBOLS_AS_DATAFRAME % {
            "symbols": "'" + "','".join(items) + "'",
            "dates": "'" + "','".join(days_of_month) + "'"
        }
        df = pd.read_sql(query, connection)
        return df

    def get_efficient_frontier(self, portfolio: List[str]):
        self.__load_symbols(portfolio)
        df = self.get_monthly_symbols_as_dataframe(portfolio)
        df['date_time'] = pd.to_datetime(df['date_time'])
        df = df.set_index('date_time')
        df = df.pivot(columns='symbol')
        df = df.fillna(method='ffill')
        df = df.fillna(method='bfill')
        # df = df.dropna()
        column_names = [x[1] for x in list(df)]

        returns_monthly = df.pct_change()
        returns_monthly = returns_monthly.replace([np.inf], 1.0)
        returns_mean = returns_monthly.mean()
        annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
        covariance = returns_monthly.cov() * 12.0

        returns_min = annualized_return.min()
        returns_max = annualized_return.max()
        target = np.linspace(returns_min, returns_max, 100)

        self.pool.map(efficient_return, [(annualized_return, covariance, order, ret) for order, ret in enumerate(target)])

        returned = 0
        efficient_portfolios = []
        while True:
            efficient_portfolios.append(self.queue.get(True))
            returned += 1
            if returned == len(target):
                break

        efficient_portfolios = sorted(efficient_portfolios, key=lambda x: x[0])
        x_vals, portfolios = [], []
        for p in efficient_portfolios:
            x_vals.append(p[1]['fun'])
            portfolios.append(p[1].x)
        x_vals = np.array(x_vals)
        y_vals = target
        sharpe = y_vals / x_vals
        return np.column_stack((x_vals, y_vals, sharpe, portfolios)), column_names

    def save_efficient_portfolio_stats(self, key, portfolios: np.ndarray, symbols: list):
        from ..models import OptimizedPortfolio
        data = {
            "portfolios": portfolios.tolist(),
            "symbols": symbols
        }
        try:
            o = OptimizedPortfolio.objects.get(portfolio_id=key)
            o.efficient_portfolio = data
        except OptimizedPortfolio.DoesNotExist:
            o = OptimizedPortfolio(portfolio_id=key, efficient_portfolio=data)
        o.save()

    def save_monthly_portfolio_stats(self, key, asset_risk: np.ndarray, asset_reward: np.ndarray, assets: list):
        from ..models import MonthlyPortfolioStats
        data = {
            "asset_risk": list(asset_risk),
            "asset_reward": list(asset_reward),
            "assets": list(assets)
        }
        try:
            o = MonthlyPortfolioStats.objects.get(portfolio_id=key)
            o.portfolio_stats = data
        except MonthlyPortfolioStats.DoesNotExist:
            o = MonthlyPortfolioStats(portfolio_id=key, portfolio_stats=data)
        o.save()

    def save_random_portfolios(self, key, portfolios: np.ndarray, column_names: List[str], returns_monthly: pd.DataFrame,
                               returns_mean: pd.Series, annualized_return: pd.Series, covariance: pd.DataFrame):
        from ..models import MonthlyPortfolioStats
        returns_monthly = returns_monthly.fillna(value=0.0)
        data = {
            "portfolios": portfolios.tolist(),
            "column_names": column_names,
            "returns_monthly": returns_monthly.to_dict('split'),
            "returns_mean": returns_mean.tolist(),
            "annualized_return": annualized_return.tolist(),
            "covariance": covariance.to_dict('split')
        }
        for i, item in enumerate(data['returns_monthly']['index']):
            data['returns_monthly']['index'][i] = item.timestamp()
        try:
            o = MonthlyPortfolioStats.objects.get(portfolio_id=key)
            o.portfolio_stats = data
        except MonthlyPortfolioStats.DoesNotExist:
            o = MonthlyPortfolioStats(portfolio_id=key, portfolio_stats=data)
        o.save()

    def get_random_portfolios(self, portfolio: List[str]) -> Tuple[np.ndarray, list, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        self.__load_symbols(portfolio)

        risk_free_asset_return = 0.0

        df = self.get_monthly_symbols_as_dataframe(portfolio)
        df['date_time'] = pd.to_datetime(df['date_time'])
        df = df.set_index('date_time')
        df = df.pivot(columns='symbol')
        df = df.dropna()
        column_names = [x[1] for x in list(df)]

        returns_monthly = df.pct_change()
        returns_mean = returns_monthly.mean()
        annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
        covariance = returns_monthly.cov() * 12.0

        portfolios = []
        portfolio_risk = []
        portfolio_return = []
        sharpe_ratio = []

        rows, columns = df.shape
        num_assets = columns
        num_portfolios = 50000

        to_compute = num_portfolios / os.cpu_count()
        pool_args = [(risk_free_asset_return, int(to_compute), num_assets, annualized_return, covariance)
                     for _ in range(os.cpu_count())]
        self.pool.map(compute_portfolio, pool_args)

        returned = 0
        while True:
            return_vals = self.queue.get(True)
            for returns in return_vals:
                a, b, c, d = returns
                portfolios.append(a)
                portfolio_risk.append(b)
                portfolio_return.append(c)
                sharpe_ratio.append(d)

            returned += 1
            if returned == os.cpu_count():
                break

        return np.column_stack((
            np.array(portfolios),
            np.array(portfolio_risk),
            np.array(portfolio_return),
            np.array(sharpe_ratio)
        )), column_names, returns_monthly, returns_mean, annualized_return, covariance
    #
    # def get_risk_free_frontier(self, portfolio: dict):
    #     self.__load_symbols(portfolio)
    #     risk_free_return = 0.0
    #     risk_free_symbol = ""
    #     if "risk_free" in portfolio:
    #         if "symbol" in portfolio["risk_free"]:
    #             risk_free_return = portfolio["risk_free"]["perc"] / 100
    #             risk_free_symbol = portfolio["risk_free"]["symbol"]
    #
    #     df = self.db.get_monthly_symbols_as_dataframe(portfolio["symbols"])
    #     df['date_time'] = pd.to_datetime(df['date_time'])
    #     df = df.set_index('date_time')
    #     df = df.pivot(columns='symbol')
    #     df = df.dropna()
    #     column_names = [x[1] for x in list(df)]
    #
    #     returns_monthly = df.pct_change()
    #     returns_monthly["adjusted_close/" + risk_free_symbol] = risk_free_return / 12.0
    #     returns_mean = returns_monthly.mean()
    #     annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
    #     covariance = returns_monthly.cov() * 12.0
    #
    #     returns_min = annualized_return.min()
    #     returns_max = annualized_return.max()
    #     target = np.linspace(returns_min, returns_max, 100)
    #
    #     self.pool.map(efficient_return,
    #                   [(annualized_return, covariance, order, ret) for order, ret in enumerate(target)])
    #
    #     returned = 0
    #     efficient_portfolios = []
    #     while True:
    #         efficient_portfolios.append(self.queue.get(True))
    #         returned += 1
    #         if returned == len(target):
    #             break
    #
    #     efficient_portfolios = sorted(efficient_portfolios, key=lambda x: x[0])
    #     x_vals, portfolios = [], []
    #     for p in efficient_portfolios:
    #         x_vals.append(p[1]['fun'])
    #         portfolios.append(p[1].x)
    #     x_vals = np.array(x_vals)
    #     y_vals = target
    #     sharpe = (y_vals) / x_vals
    #     return np.column_stack((x_vals, y_vals, sharpe, portfolios)), column_names


@shared_task
def optimize_portfolio(portfolio: List[str]):
    symbol_string = "_".join(sorted(portfolio))
    portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()
    optimizer = PortfolioOptimizer()
    efficient_frontier, symbols = optimizer.get_efficient_frontier(portfolio)
    optimizer.save_efficient_portfolio_stats(portfolio_key, efficient_frontier, symbols)
    asset_risk, asset_reward, assets = optimizer.get_monthly_portfolio_stats(portfolio)
    optimizer.save_monthly_portfolio_stats(portfolio_key, asset_risk, asset_reward, assets)
    portfolios, *others = optimizer.get_random_portfolios(portfolio)
    optimizer.save_random_portfolios(portfolio_key + "_random", portfolios, others[0], others[1], others[2], others[3], others[4])
    optimizer.pool.close()
    print("done")

