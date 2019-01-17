import datetime, csv
import requests, json, time, os
import numpy as np
from numpy.core.multiarray import ndarray
from pandas import DataFrame

from utils import Db
import pandas as pd
from typing import List, Set, Dict, Tuple, Optional
from multiprocessing import Queue, Pool
from utils.EFC import portfolio_volatility
from scipy import optimize

def pool_init(queue):
    global q
    q = queue


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


class AlphaVantage:

    date_key = '%Y-%m-%d'
    api_function = 'TIME_SERIES_DAILY_ADJUSTED'
    error_text = "Error Message"
    time_series_key = 'Time Series (Daily)'
    open_key = "1. open"
    closed_key = "4. close"
    ENDPOINT = 'https://www.alphavantage.co/query'

    def __init__(self, apikey: str, requests_per_minute=5,
                 cache_folder="cache"):
        self.cache_folder = cache_folder
        self.requests_per_minute = requests_per_minute
        self.apikey = apikey
        self.rpm = 0
        self.db = Db(cache_folder)
        self.mem = {}
        self.queue = Queue()
        self.pool = Pool(initializer=pool_init, initargs=(self.queue,), processes=os.cpu_count())

    def _load_symbols(self, portfolio: dict):
        if "symbols" not in portfolio: raise Exception("Missing symbols")
        symbols = portfolio["symbols"]  # type: list
        for symbol in symbols:
            self.__load_symbol(symbol)

    def get_monthly_portfolio_stats(self, portfolio: dict)->Tuple[np.ndarray, np.ndarray, list]:
        self._load_symbols(portfolio)
        df = self.db.get_monthly_symbols_as_dataframe(portfolio["symbols"])
        df['date_time'] = pd.to_datetime(df['date_time'])
        df = df.set_index('date_time')
        df = df.pivot(columns='symbol')
        df = df.dropna()
        column_names = [x[1] for x in list(df)]

        returns_monthly = df.pct_change()
        returns_mean = returns_monthly.mean().as_matrix()
        annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
        std = returns_monthly.std().as_matrix() * np.sqrt(12.0)
        return std, annualized_return, column_names

    def get_random_portfolios(self, portfolio: dict)->Tuple[np.ndarray, list, pd.DataFrame, pd.DataFrame, pd.DataFrame,
                                                            pd.DataFrame]:
        self._load_symbols(portfolio)

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
        self._load_symbols(portfolio)
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

    def get_efficient_frontier(self, portfolio: dict):
        self._load_symbols(portfolio)
        risk_free_asset_return = 0.0
        if "risk_free_asset_return_percentage" in portfolio:
            risk_free_asset_return = portfolio["risk_free_asset_return_percentage"] / 100
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
        sharpe = (y_vals - risk_free_asset_return) / x_vals
        return np.column_stack((x_vals, y_vals, sharpe, portfolios)), column_names

    def __load_symbol(self, symbol):
        if self.rpm == self.requests_per_minute:
            print("waiting")
            time.sleep(60)
            self.rpm = 0

        if not self.db.has_request_today(symbol):
            r = requests.get(url=self.ENDPOINT, params={
                'apikey': self.apikey,
                'function': self.api_function,
                'symbol': symbol,
                'outputsize': 'full'
            })
            data = r.json()
            if self.time_series_key in data:
                combined = data[self.time_series_key]
                record = []
                for date in combined:
                    record.append([
                        symbol,
                        datetime.datetime.strptime(date, '%Y-%m-%d').timestamp(),
                        float(combined[date]['3. low']),
                        float(combined[date]['7. dividend amount']),
                        float(combined[date]['5. adjusted close']),
                        float(combined[date]['1. open']),
                        float(combined[date]['8. split coefficient']),
                        float(combined[date]['4. close']),
                        float(combined[date]['2. high']),
                        float(combined[date]['6. volume'])
                    ])
                self.db.insert_alpha_vantage_records(record)
                date_string = datetime.datetime.today().strftime(self.date_key)
                today = int(datetime.datetime.strptime(date_string, self.date_key).timestamp())
                self.db.insert_alpha_vantage_api_request(today, symbol)
            self.rpm += 1
