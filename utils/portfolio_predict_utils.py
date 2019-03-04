import os
from datetime import datetime, timedelta
import hashlib
import json
from multiprocessing import Queue, Pool
from typing import Tuple

import ta
from scipy.signal import argrelextrema
from sklearn import preprocessing
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from auto_trading import AutoTrader
from utils.db.Db import Db
import pandas as pd
import numpy as np
import keras.backend as K


class Dataset:
    def __init__(
            self,
            df: pd.DataFrame,
            df_source: pd.DataFrame,
            dates,
            maxes_dates,
            maxes_vals,
            mins_dates,
            mins_vals,
            target
    ):
        self.mins_vals = mins_vals
        self.mins_dates = mins_dates
        self.maxes_vals = maxes_vals
        self.maxes_dates = maxes_dates
        self.dates = dates
        self.df_source = df_source
        self.df = df
        self.target = target


class TrainTestData:
    def __init__(
            self,
            x_train_scaled,
            y_train,
            x_test_scaled,
            x_test,
            y_test,
            testing_data
    ):
        self.testing_data = testing_data
        self.y_test = y_test
        self.x_test = x_test
        self.x_test_scaled = x_test_scaled
        self.y_train = y_train
        self.x_train_scaled = x_train_scaled

    def as_conv(self)->Tuple[np.array, np.array, Tuple[int, int, int]]:
        x_train = self.x_train_scaled.astype(np.float32)
        x_test = self.x_test_scaled.astype(np.float32)
        stride = len(AutoTrader.columns) - 1
        train_height = int(len(x_train[0]) / stride)
        test_height = int(len(x_test[0]) / stride)

        if K.image_data_format() == 'channels_first':
            x_train = x_train.reshape(x_train.shape[0], 1, train_height, int(stride))
            x_test = x_test.reshape(x_test.shape[0], 1, test_height, int(stride))
            input_shape = (1, train_height, 56)
        else:
            x_train = x_train.reshape(x_train.shape[0], train_height, int(stride), 1)
            x_test = x_test.reshape(x_test.shape[0], test_height, int(stride), 1)
            input_shape = (train_height, 56, 1)
        return x_train, x_test, input_shape


def plot(sd: Dataset, test_dates, test_output):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    days = mdates.DayLocator()
    yearsFmt = mdates.DateFormatter('%Y-%m-%d')
    fig = plt.figure()
    ax = fig.add_subplot(211)

    data_plot = sd.df_source[sd.df_source['symbol'] == sd.target]['adjusted_close']
    ax.scatter(sd.dates, data_plot, label='Price', s=2)
    ax.scatter(sd.maxes_dates, sd.maxes_vals.tolist(), label='Maxes', s=10, color='red')
    ax.scatter(sd.mins_dates, sd.mins_vals.tolist(), label='Mins', s=10, color='green')

    plt.title('Data')

    ax = fig.add_subplot(212, sharex=ax)
    ax.scatter(test_dates, test_output)

    left = sd.dates[-365]
    right = sd.dates[-1] + timedelta(days=5)
    ax.set_xlim(left=left, right=right)

    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_minor_locator(days)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    fig.autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()


def make_training_testing_datasets(df: pd.DataFrame)->TrainTestData:
    training_data = df[df['date_time'] < datetime.now() - timedelta(days=365)]
    training_data = training_data.as_matrix()
    x_train = training_data[:, 1:-1]
    y_train = training_data[:, -1].astype(int)

    testing_data = df[df['date_time'] >= datetime.now() - timedelta(days=365)]
    testing_data = testing_data.as_matrix()
    x_test = testing_data[:, 1:-1]
    y_test = testing_data[:, -1].astype(int)

    scaler = preprocessing.StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)
    return TrainTestData(x_train_scaled, y_train, x_test_scaled, x_test, y_test, testing_data)


def make_max_sharpe_dataset(sector="Communication Services")->Dataset:
    db = Db("../cache")
    snp = pd.read_csv("../cache/s&p500_companies.csv")
    port = {
        "name": sector,
        "symbols": list(snp[snp['GICS Sector'] == sector]['Symbol'])
    }
    symbol_string = "_".join(port["symbols"])
    portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()
    efficient = db.get_monthly_portfolio_stats(portfolio_key + "_efficient")
    efficient = json.loads(efficient)
    efficient['portfolios'] = np.array(efficient['portfolios'], dtype=float)
    msr = pd.DataFrame(
        efficient['portfolios'][
            np.where(efficient['portfolios'][:, 2] == np.max(efficient['portfolios'][:, 2]))
        ][:, 3:], columns=efficient['symbols']).transpose()
    msr = msr[msr[0].round(2) > 0.00]
    msr = msr.reset_index()
    msr.columns = ['symbol', 'allocation']
    target = msr['symbol'][msr['allocation'] == msr['allocation'].min()].iloc[0]
    return make_dataset(db, list(msr['symbol']), target)


def make_sector_dataset(target="AAPL")->Dataset:
    db = Db("../cache")
    snp = pd.read_csv("../cache/s&p500_companies.csv")
    sector_name = snp[snp['Symbol'] == target]['GICS Sector'].as_matrix()[0]
    sector = snp[snp['GICS Sector'] == sector_name].as_matrix()
    return make_dataset(db, list(sector[:, 1]), target)


def pool_init(queue):
    global q
    q = queue


def add_all_ta_features(args):
    i, next_df, symbol = args
    try:
        next_df = ta.add_all_ta_features(next_df, "open", "high", "low", "adjusted_close", "volume", fillna=True)
        next_df.pop("symbol")
        columns = AutoTrader.columns.copy()
        columns.pop()
        next_df = next_df[columns]
        q.put((i, next_df, symbol))
    except IndexError as e:
        print(e)


def make_dataset(db: Db, symbols: list, target: str)->Dataset:
    df_source, others = db.get_symbols_ten_year(symbols)
    others.pop(others.index(target))
    others = pd.Series(others)
    df_source['date_time'] = pd.to_datetime(df_source['date_time'])
    df_source = df_source.set_index('date_time')
    df = df_source[df_source['symbol'] == target].copy()
    df = ta.add_all_ta_features(df, "open", "high", "low", "adjusted_close", "volume", fillna=True)
    dates = df.index
    mins = argrelextrema(df['adjusted_close'].as_matrix(), np.less, order=5)
    mins_dates = dates[mins[0]]
    mins_vals = df['adjusted_close'].as_matrix()[mins[0]]
    maxes = argrelextrema(df['adjusted_close'].as_matrix(), np.greater, order=5)
    maxes_dates = dates[maxes[0]]
    maxes_vals = df['adjusted_close'].as_matrix()[maxes[0]]
    df['make_a_trade'] = 0
    df['make_a_trade'][mins_dates] = 1
    df['make_a_trade'][maxes_dates] = 2
    df = df[AutoTrader.columns]

    pool_args = []
    for i, symbol in enumerate(others):
        next_df = df_source[df_source['symbol'] == symbol].copy()
        pool_args.append((i, next_df, symbol))

    queue = Queue()
    pool = Pool(initializer=pool_init, initargs=(queue,), processes=os.cpu_count() - 1)
    pool.map(add_all_ta_features, pool_args)
    return_vals = []
    done = 0
    while True:
        return_vals.append(queue.get(True))
        done += 1
        if done == len(pool_args):
            break
    return_vals.sort(key=lambda x: x[0])
    for i, next_df, symbol in return_vals:
        df = df.join(next_df, how='inner', rsuffix='_' + symbol)

    mat = df.pop('make_a_trade')
    df['make_a_trade'] = mat
    df = df.reset_index()
    pool.close()
    return Dataset(df, df_source, dates, maxes_dates, maxes_vals, mins_dates, mins_vals, target)
