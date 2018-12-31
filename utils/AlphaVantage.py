import datetime, csv
import requests, json, time, os
import numpy as np
from numpy.core.multiarray import ndarray
from pandas import DataFrame

from utils import Db
import pandas as pd
from typing import List, Set, Dict, Tuple, Optional
import random
from itertools import permutations
from multiprocessing import Queue, Pool

q = Queue()


def compute_portfolio(all_inputs):
    symbols, mean, std, coeffs = all_inputs
    weights = np.random.random(len(symbols))
    weights /= np.sum(weights)
    returns = np.dot(weights, mean)

    pfd = np.dot(weights ** 2, std.T ** 2)
    pfd1 = 0.0
    weights = pd.Series(weights, index=symbols)
    computed = []
    for symbol in symbols:
        for symbol1 in symbols:
            if symbol != symbol1 and sorted((symbol, symbol1)) not in computed:
                cor = coeffs[symbol][symbol1]
                pfd1 += 2 * weights[symbol] * std[symbol] * weights[symbol1] * std[symbol1] * cor
                computed.append(sorted((symbol, symbol1)))

    risk = np.sqrt(pfd + pfd1)
    q.put((weights, risk, returns))


class AlphaVantage:

    date_key = '%Y-%m-%d'
    api_function = 'TIME_SERIES_DAILY_ADJUSTED'
    error_text = "Error Message"
    time_series_key = 'Time Series (Daily)'
    open_key = "1. open"
    closed_key = "4. close"
    ENDPOINT = 'https://www.alphavantage.co/query'

    def __init__(self, apikey: str, preload_cache=True, requests_per_minute=5,
                 cache_folder="cache"):
        self.cache_folder = cache_folder
        self.requests_per_minute = requests_per_minute
        self.apikey = apikey
        self.rpm = 0
        self.db = Db(cache_folder)
        self.mem = {}

    def get_monthly_portfolio_stats(self, portfolio: dict)->Tuple[np.ndarray, np.ndarray, float, float]:
        if "symbols" not in portfolio: raise Exception("Missing symbols")
        mean, std, corr, symbols, remove, combined = self.get_monthly_stats(portfolio)  
        w = {}
        if "weights" in portfolio:
            w = portfolio["weights"]
        else:
            weight = 100.0 / float(len(symbols)) / 100.0
            for symbol in symbols:
                w[symbol] = weight

        weights = pd.Series([w[symbol] for symbol in symbols], index=symbols)

        returns = np.dot(weights, mean)  # type: float
        pfd = np.dot(weights ** 2, std.T ** 2)
        pfd1 = 0.0
        weights = pd.Series(weights, index=symbols)
        computed = []
        for symbol in symbols:
            for symbol1 in symbols:
                if symbol != symbol1 and sorted((symbol, symbol1)) not in computed:
                    cor = corr[symbol][symbol1]
                    pfd1 += 2 * weights[symbol] * std[symbol] * weights[symbol1] * std[symbol1] * cor
                    computed.append(sorted((symbol, symbol1)))
        risk = np.sqrt(pfd + pfd1)
        stdr = std.as_matrix()  # type: np.ndarray
        mr = mean.as_matrix() # type: np.ndarray
        return stdr, mr, risk, returns

    def get_random_portfolios(self, portfolio: dict)->Tuple[np.ndarray, list, list]:
        if "symbols" not in portfolio: raise Exception("Missing symbols")
        mean, std, coeffs, symbols, remove, combined = self.get_monthly_stats(portfolio)

        pool = Pool(processes=os.cpu_count())
        pool.map(compute_portfolio, [(symbols, mean, std, coeffs) for x in range(10000)])

        portfolios = []
        portfolio_risk = []
        portfolio_return = []
        while not q.empty():
            a, b, c = q.get(True)
            portfolios.append(a)
            portfolio_risk.append(b)
            portfolio_return.append(c)
        pool.close()

        return np.column_stack((np.array(portfolios), np.array(portfolio_risk), np.array(portfolio_return))), symbols, \
            remove

    def get_monthly_stats(self, portfolio: dict)->Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list, list, pd.DataFrame]:
        if "symbols" not in portfolio: raise Exception("Missing symbols")
        symbols = portfolio["symbols"]  # type: list
        if tuple(symbols) in self.mem:
            return self.mem[tuple(symbols)]
        for symbol in symbols:
            self.__load_symbol(symbol)

        df = self.db.get_symbols_as_dataframe(portfolio["symbols"])
        returns = []
        remove = []
        for symbol in symbols:
            sdf = df[df['symbol'] == symbol]
            try:
                if sdf.shape[0] < 1:
                    raise ValueError()
                returns.append(self._compute_monthly_returns(sdf, symbol))
            except ValueError as e:
                remove.append(symbol)
        for symbol in remove:
            symbols.remove(symbol)

        combined = returns[0].set_index('month')
        for num, symbol in enumerate(symbols):
            if num > 0:
                combined = combined.join(
                    returns[num].set_index('month'),
                    how='inner'
                )
        combined = combined.reset_index()
        del returns

        mean = combined.mean()
        std = combined.std()

        coeffs = combined.set_index('month').T.as_matrix()
        coeffs = pd.DataFrame(np.corrcoef(coeffs), columns=symbols)
        coeffs['symbols'] = symbols
        coeffs = coeffs.set_index('symbols')

        self.mem[tuple(symbols)] = mean, std, coeffs, symbols, remove, combined
        return mean, std, coeffs, symbols, remove, combined

    def _compute_monthly_returns(self, df: pd.DataFrame, symbol: str)->pd.DataFrame:
        years = sorted(list(set(list(df["year"]))))

        returns = []
        for year_num in years:
            year_data = df[df["year"] == year_num].sort_values(['month', 'day'], ascending=[1, 1])
            months = sorted(list(set(list(year_data["month"]))))

            for month_num in months:
                month_data = year_data[year_data["month"] == month_num]
                if month_data.shape[0] > 1:
                    start = month_data["open"].iloc[0]
                    end = month_data.tail()["close"].iloc[0]
                    returns.append([
                        datetime.datetime(year=year_num, month=month_num, day=1),
                        ((end - start) / start) * 100.00
                    ])
        returns = pd.DataFrame(returns)
        returns.columns = ['month', str(symbol)]
        return returns

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