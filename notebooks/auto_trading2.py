import os
import sys

import ta
from ta import add_all_ta_features

sys.path.append("..")
from utils import Db
import pandas as pd
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

db = Db("../cache")
df = db.get_symbols_as_dataframe(['AAPL'])
df['date_time'] = pd.to_datetime(df['date_time'])

df['stochastic_oscilator'] = ta.stoch(df['high'], df['low'], df['adjusted_close'])
df['stochastic_signal'] = ta.stoch_signal(df['high'], df['low'], df['adjusted_close'])
df['macd_line'] = ta.macd(df['adjusted_close'])
df['macd_signal'] = ta.macd_signal(df['adjusted_close'])
df['macd_hist'] = ta.macd_diff(df['adjusted_close'])
df = df.dropna()

# df = df[df['date_time'] > datetime.now() - timedelta(days=365)]
df = df.reset_index()

scatter_data = df[['unix_time', 'adjusted_close', 'date_time']].as_matrix()
dates = scatter_data[:, 2]
# 113275.45 275458.53 106815.84
start_money = 100000.
current_money = start_money
shares = 0.
buy_signals, sell_signals = [], []
for i, current_macd in enumerate(df['macd_line']):
    if i > 0:
        macd_buy = False
        stoch_buy = False

        # buy signal
        if df['macd_line'].loc[i - 1] < 0 < df['macd_line'].loc[i]:
            macd_buy = True

        if df['stochastic_oscilator'].loc[i] <= 20:
            stoch_buy = True

        if macd_buy and stoch_buy:
            buy_signals.append(scatter_data[i, 2])
            current_price = df['adjusted_close'].loc[i]
            buying = np.floor(current_money / current_price)
            shares += buying
            current_money -= buying * current_price

        macd_sell = False
        stoch_sell = False
        # sell signal
        if df['macd_line'].loc[i - 1] > 0 > df['macd_line'].loc[i]:
            macd_sell = True

        if df['stochastic_oscilator'].loc[i] >= 80:
            stoch_sell = True

        if macd_sell and stoch_sell:
            sell_signals.append(scatter_data[i, 2])
            current_price = df['adjusted_close'].loc[i]
            current_money += current_price * shares
            shares = 0

end_price = df['adjusted_close'][df.index[-1]]
extra_money = shares * end_price
current_money += extra_money
start_price = df['adjusted_close'].loc[0]
start_shares = np.floor(start_money / start_price)
end_money = end_price * start_shares
print("Auto Trading: $" + str(current_money))
print("Buy and Hold: $" + str(end_money))

years = mdates.YearLocator()  # every year
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator()
yearsFmt = mdates.DateFormatter('%Y-%m-%d')
fig = plt.figure()
ax = fig.add_subplot(311)
ax.scatter(dates, scatter_data[:, 1].tolist(), label='Price', s=2)
# ax.plot(dates, days_12['adjusted_close'], label='12 Days Moving Average', color='red')
# ax.plot(dates, days_26['adjusted_close'], label='26 Days Moving Average', color='green')

for date in buy_signals:
    ax.axvline(date, color=[.78, .83, .89, 1.0])
for date in sell_signals:
    ax.axvline(date, color=[1.0, .89, .89, 1.0])



plt.title('MACD indicator')
plt.legend()

ax = fig.add_subplot(312, sharex=ax)
ax.plot(dates, df['macd_line'], label='MACD Line', color='blue')
ax.plot(dates, df['macd_signal'], label='Signal Line', color='red')
colors = ["green" if x > 0 else "red" for x in df['macd_hist']]
ax.bar(dates, df['macd_hist'], label='MACD Hist', color=colors)

ax.axhline(0)

ax = fig.add_subplot(313, sharex=ax)
ax.plot(dates, df['stochastic_oscilator'], label='Stochastic Oscilator', color='blue')
ax.plot(dates, df['stochastic_signal'], label='Signal Line', color='red')

ax.xaxis.set_major_locator(years)
ax.xaxis.set_minor_locator(months)
ax.xaxis.set_major_formatter(yearsFmt)
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.axhline(80)
ax.axhline(20)

fig.tight_layout()
fig.subplots_adjust(hspace=0)
fig.autofmt_xdate()
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
