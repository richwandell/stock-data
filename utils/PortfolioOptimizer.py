from typing import List, Tuple
import numpy as np
import pandas as pd
from multiprocessing import Queue, Pool
import os
from scipy import optimize

from utils import NoAPIClientException, APIFailedException
from utils.Exceptions import APIRateLimitException
from utils.db.Db import MySQLDb
from utils.api.StockPriceAPIClient import StockPriceAPIClient
from utils.EFC import portfolio_volatility


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
    result = optimize.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
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

    def __init__(self, db: MySQLDb, api_client_list: List[StockPriceAPIClient], offline=False):
        self.api_client_list = api_client_list
        self.db = db
        self.failed_api_clients = {}
        self.queue = Queue()
        self.pool = Pool(initializer=pool_init, initargs=(self.queue,), processes=os.cpu_count())
        self.offline = offline

    def get_monthly_portfolio_stats(self, portfolio: dict)->Tuple[np.ndarray, np.ndarray, list]:
        self.__load_symbols(portfolio)
        df = self.db.get_monthly_symbols_as_dataframe(portfolio["symbols"])
        df['date_time'] = pd.to_datetime(df['date_time'])
        df = df.set_index('date_time')
        df = df.pivot(columns='symbol')
        df = df.fillna(method='ffill')
        df = df.fillna(method='bfill')
        column_names = [x[1] for x in list(df)]

        returns_monthly = df.pct_change()
        returns_monthly = returns_monthly.replace([np.inf], 1.0)
        returns_mean = returns_monthly.mean().as_matrix()
        annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
        std = returns_monthly.std().as_matrix() * np.sqrt(12.0)
        return std, annualized_return, column_names

    def __load_symbols(self, portfolio: dict):
        if self.offline: return
        if "symbols" not in portfolio: raise Exception("Missing symbols")
        symbols = portfolio["symbols"]  # type: list
        for symbol in symbols:
            self.__load_symbol(symbol)

    def __load_symbol(self, symbol):
        if len(self.api_client_list) == 0:
            raise NoAPIClientException

        if not self.db.has_request_today(symbol):
            remove = False
            for i, api_client in enumerate(self.api_client_list):
                try:
                    api_client.load_symbol(symbol)
                    break
                except APIRateLimitException as e:
                    remove = i

            if remove is not False:
                del self.api_client_list[remove]

    def get_efficient_frontier(self, portfolio: dict):
        self.__load_symbols(portfolio)

        df = self.db.get_monthly_symbols_as_dataframe(portfolio["symbols"])
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

    def get_random_portfolios(self, portfolio: dict)->Tuple[np.ndarray, list, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        self.__load_symbols(portfolio)

        risk_free_asset_return = 0.0
        if "risk_free" in portfolio:
            if "perc" in portfolio["risk_free"]:
                risk_free_asset_return = portfolio["risk_free"]["perc"] / 100

        df = self.db.get_monthly_symbols_as_dataframe(portfolio["symbols"])
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

    def get_risk_free_frontier(self, portfolio: dict):
        self.__load_symbols(portfolio)
        risk_free_return = 0.0
        risk_free_symbol = ""
        if "risk_free" in portfolio:
            if "symbol" in portfolio["risk_free"]:
                risk_free_return = portfolio["risk_free"]["perc"] / 100
                risk_free_symbol = portfolio["risk_free"]["symbol"]

        df = self.db.get_monthly_symbols_as_dataframe(portfolio["symbols"])
        df['date_time'] = pd.to_datetime(df['date_time'])
        df = df.set_index('date_time')
        df = df.pivot(columns='symbol')
        df = df.dropna()
        column_names = [x[1] for x in list(df)]

        returns_monthly = df.pct_change()
        returns_monthly["adjusted_close/" + risk_free_symbol] = risk_free_return / 12.0
        returns_mean = returns_monthly.mean()
        annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
        covariance = returns_monthly.cov() * 12.0

        returns_min = annualized_return.min()
        returns_max = annualized_return.max()
        target = np.linspace(returns_min, returns_max, 100)

        self.pool.map(efficient_return,
                      [(annualized_return, covariance, order, ret) for order, ret in enumerate(target)])

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
        sharpe = (y_vals) / x_vals
        return np.column_stack((x_vals, y_vals, sharpe, portfolios)), column_names
