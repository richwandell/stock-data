import ta
from scipy.signal import argrelextrema
import os
import sys

from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier


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
df = ta.add_all_ta_features(df, 'open', 'high', 'low', 'adjusted_close', 'volume')
scatter_data = df[['unix_time', 'adjusted_close', 'date_time']].as_matrix()
dates = scatter_data[:, 2]

df['make_a_trade'] = 0

mins = argrelextrema(df['adjusted_close'].as_matrix(), np.less, order=5)
mins_dates = dates[mins[0]]
mins_vals = scatter_data[mins[0], 1]
maxes = argrelextrema(df['adjusted_close'].as_matrix(), np.greater, order=5)
maxes_dates = dates[maxes[0]]
maxes_vals = scatter_data[maxes[0], 1]

df = df.set_index('date_time')
df['make_a_trade'][mins_dates] = 1
df['make_a_trade'][maxes_dates] = 2
df = df.dropna()
columns = ['volume_adi', 'volume_obv', 'volume_obvm', 'volume_cmf', 'volume_fi', 'volume_em', 'volume_vpt',
           'volume_nvi', 'volatility_atr', 'volatility_bbh', 'volatility_bbl', 'volatility_bbm', 'volatility_bbhi',
           'volatility_bbli', 'volatility_kcc', 'volatility_kch', 'volatility_kcl', 'volatility_kchi',
           'volatility_kcli', 'volatility_dch', 'volatility_dcl', 'volatility_dchi', 'volatility_dcli', 'trend_macd',
           'trend_macd_signal', 'trend_macd_diff', 'trend_ema_fast', 'trend_ema_slow', 'trend_adx', 'trend_adx_pos',
           'trend_adx_neg', 'trend_vortex_ind_pos', 'trend_vortex_ind_neg', 'trend_vortex_diff', 'trend_trix',
           'trend_mass_index', 'trend_cci', 'trend_dpo', 'trend_kst', 'trend_kst_sig', 'trend_kst_diff',
           'trend_ichimoku_a', 'trend_ichimoku_b', 'trend_visual_ichimoku_a', 'trend_visual_ichimoku_b',
           'trend_aroon_up', 'trend_aroon_down', 'trend_aroon_ind', 'momentum_rsi', 'momentum_mfi', 'momentum_tsi',
           'momentum_uo', 'momentum_stoch', 'momentum_stoch_signal', 'momentum_wr', 'momentum_ao', 'make_a_trade']
df = df.reset_index()
training_data = df[df['date_time'] < datetime.now() - timedelta(days=365)]
training_data = training_data[columns].as_matrix()
x_train = training_data[:, 0:-1]
y_train = training_data[:, -1].astype(int)

testing_data = df[df['date_time'] >= datetime.now() - timedelta(days=365)]
testing_data = testing_data[columns].as_matrix()
x_test = testing_data[:, 0:-1]
y_test = testing_data[:, -1].astype(int)

scaler = preprocessing.StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)

svc_rbf = SVC(kernel='rbf', class_weight='balanced', verbose=True)
svc_rbf.fit(x_train_scaled, y_train)

# 100 = 0.56, 0.2
mlpc = MLPClassifier(
    verbose=True,
    hidden_layer_sizes=(200, 20),
    tol=1e-10,
    alpha=0.001,
    learning_rate='adaptive'
)
mlpc.fit(x_train_scaled, y_train)

x_test_scaled = scaler.transform(x_test)
test_output = svc_rbf.predict(x_test_scaled)
errors = np.abs(y_test - test_output)
print(np.std(errors))
print(np.mean(errors))

test_output_mlp = mlpc.predict(x_test_scaled)
errors = np.abs(y_test - test_output_mlp)
print(np.std(errors))
print(np.mean(errors))


years = mdates.YearLocator()  # every year
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator()
yearsFmt = mdates.DateFormatter('%Y-%m-%d')
fig = plt.figure()
ax = fig.add_subplot(211)

ax.scatter(dates, scatter_data[:, 1].tolist(), label='Price', s=2)
ax.scatter(maxes_dates, maxes_vals.tolist(), label='Maxes', s=10, color='red')
ax.scatter(mins_dates, mins_vals.tolist(), label='Mins', s=10, color='green')

test_dates = dates[-len(testing_data):]

for i, date in enumerate(test_dates):
    if test_output[i] == 1:
        ax.axvline(date, color=[.78, .83, .89, 1.0])
    elif test_output[i] == 2:
        ax.axvline(date, color=[1.0, .89, .89, 1.0])


plt.ylabel('Price')
plt.title('Data')

ax = fig.add_subplot(212, sharex=ax)
ax.plot(test_dates, test_output)

left = dates[-365]
right = dates[-1] + timedelta(days=5)
ax.set_xlim(left=left, right=right)

ax.xaxis.set_major_locator(years)
ax.xaxis.set_minor_locator(months)
ax.xaxis.set_major_formatter(yearsFmt)
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

fig.tight_layout()
fig.subplots_adjust(hspace=0)
fig.autofmt_xdate()
plt.xlabel('Date')

plt.legend()
plt.show()


start_money = 100000.
current_money = start_money
shares = 0.
for i, date in enumerate(test_dates):
    #buy signal
    svm_output = test_output_mlp[i]
    current_adjusted_close = float(df[df['date_time'] == date]['adjusted_close'])
    if svm_output == 1:
        buying = np.floor(current_money / current_adjusted_close)
        shares += buying
        current_money -= buying * current_adjusted_close
    elif svm_output == 2:
        current_money += current_adjusted_close * shares
        shares = 0

#sell all of our shares left over at the current price to get the value at the end
end_price = float(df[df['date_time'] == test_dates[-1]]['adjusted_close'])
extra_money = shares * end_price
current_money += extra_money

#calculate buy and hold
start_price = float(df[df['date_time'] == test_dates[0]]['adjusted_close'])
start_shares = np.floor(start_money / start_price)
bnh_current_money = start_money - (start_shares * start_price)
end_money = end_price * start_shares
end_money += bnh_current_money


print("Perfect Trading: $" + str(current_money))
print("Buy and Hold: $" + str(end_money))
diff = current_money - end_money
print("Perfect vs Buy and Hold: " + "+"+str(diff) if diff > 0 else diff )
print("Profit: " + (str(current_money - start_money)))
print("Number of Trades: " + str(len(mins_dates) + len(maxes_dates)))