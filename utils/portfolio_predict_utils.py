from datetime import datetime, timedelta
import hashlib
import json

import ta
from scipy.signal import argrelextrema
from sklearn import preprocessing
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from auto_trading import AutoTrader
from utils.db.Db import Db
import pandas as pd
import numpy as np

def plot(df_source, dates, target, maxes_dates, maxes_vals, mins_dates, mins_vals, test_dates, test_output):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    days = mdates.DayLocator()
    yearsFmt = mdates.DateFormatter('%Y-%m-%d')
    fig = plt.figure()
    ax = fig.add_subplot(211)

    data_plot = df_source[df_source['symbol'] == target]['adjusted_close']
    ax.scatter(dates, data_plot, label='Price', s=2)
    ax.scatter(maxes_dates, maxes_vals.tolist(), label='Maxes', s=10, color='red')
    ax.scatter(mins_dates, mins_vals.tolist(), label='Mins', s=10, color='green')

    plt.title('Data')

    ax = fig.add_subplot(212, sharex=ax)
    ax.scatter(test_dates, test_output)

    left = dates[-365]
    right = dates[-1] + timedelta(days=5)
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


def make_training_testing_datasets(df):
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
    return x_train_scaled, y_train, x_test_scaled, x_test, y_test, testing_data


def make_max_sharpe_dataset(sector="Communication Services"):
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
    msr.columns = ['symbol', 'sharpe']
    target = msr['symbol'][msr['sharpe'] == msr['sharpe'].max()].iloc[0]
    others = msr['symbol'][msr['symbol'] != target]

    df_source = db.get_symbols_as_dataframe(list(msr['symbol']))
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

    for symbol in others:
        next_df = df_source[df_source['symbol'] == symbol].copy()
        next_df = ta.add_all_ta_features(next_df, "open", "high", "low", "adjusted_close", "volume", fillna=True)
        next_df.pop("symbol")
        columns = AutoTrader.columns
        columns.pop()
        next_df = next_df[columns]
        df = df.join(next_df, how='inner', rsuffix='_' + symbol)

    mat = df.pop('make_a_trade')
    df['make_a_trade'] = mat
    df = df.reset_index()
    return df, df_source, dates, maxes_dates, maxes_vals, mins_dates, mins_vals, target
