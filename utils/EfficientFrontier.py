import os
from typing import List

import pandas as pd
from scipy import optimize

from utils.EFC import portfolio_volatility
from utils.db.Db import Db
from multiprocessing import Queue, Pool
import numpy as np


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


class EfficientFrontier:

    def __init__(self, cache_folder="cache"):
        self.cache_folder = cache_folder
        self.db = Db(cache_folder)

    def get_efficient_frontier(self, symbols: List[str]):
        queue = Queue()
        pool = Pool(initializer=pool_init, initargs=(queue,), processes=os.cpu_count())

        df = self.db.get_monthly_symbols_as_dataframe(symbols)
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

        pool.map(efficient_return, [(annualized_return, covariance, order, ret) for order, ret in enumerate(target)])

        returned = 0
        efficient_portfolios = []
        while True:
            efficient_portfolios.append(queue.get(True))
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
