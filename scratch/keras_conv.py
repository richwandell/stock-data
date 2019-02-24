import hashlib
import json
import sys
import ta
from scipy.signal import argrelextrema
sys.path.append("..")
from utils.db.Db import Db
from auto_trading import AutoTrader
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from keras.layers import Dense, Dropout, Conv2D, Flatten, MaxPooling2D
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras import backend as K
import keras
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder

"""
Attempt to use negative correlation to predict buy and sell signals
1. Collect efficient frontier maximum sharpe ratio portfolio for a category 
2. Collect all technical analysis features for symbols used in efficient portfolio
3. Compute historical maxes and mins for highest percentage symbol in efficient portfolio 
    to generate optimal buy and sell signals
4. Construct a time series dataset with all features from all symbols in efficient portfolio 
    including buy and sell signals for target symbol.
5. Train Keras Conv net to predict by and sell signals
"""
db = Db("../cache")

snp = pd.read_csv("../cache/s&p500_companies.csv")
sector = "Communication Services"
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
    ][:, 3:], columns=efficient['symbols'])\
    .transpose()
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
columns = AutoTrader.columns
columns.pop()
df = df[columns]
mins = argrelextrema(df['adjusted_close'].as_matrix(), np.less, order=5)
dates = df.index
mins_dates = dates[mins[0]]
maxes = argrelextrema(df['adjusted_close'].as_matrix(), np.greater, order=5)
maxes_dates = dates[maxes[0]]

df = df.set_index('date_time')
df['make_a_trade'] = 0
df['make_a_trade'][mins_dates] = 1
df['make_a_trade'][maxes_dates] = 2
for symbol in others:
    next_df = df_source[df_source['symbol'] == symbol].copy()
    next_df = ta.add_all_ta_features(next_df, "open", "high", "low", "adjusted_close", "volume", fillna=True)
    df = df.join(next_df, how='inner', rsuffix='_' + symbol)


print("hi")
# df = db.get_symbols_as_dataframe(['AVGO'])
# df = ta.add_all_ta_features(df, "open", "high", "low", "adjusted_close", "volume")