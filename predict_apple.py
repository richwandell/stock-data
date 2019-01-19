from utils.Db import Db
import pandas as pd
import numpy as np
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from joblib import dump, load

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')

db = Db()
df = db.get_symbols_as_dataframe(['AAPL'])
df['date_time'] = pd.to_datetime(df['date_time'])


svr_lin = SVR(kernel='linear', C=1e3)
svr_poly = SVR(kernel='poly', C=1e3, degree=2)
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
dates = df['unix_time'].as_matrix()
dates = np.reshape(dates, (len(dates), 1))
prices = df['adjusted_close'].as_matrix()
svr_rbf.fit(dates, prices)

fig, ax = plt.subplots()
ax.scatter(df['date_time'].as_matrix(), df['adjusted_close'])
ax.plot(df['date_time'].as_matrix(), svr_rbf.predict(dates), color='red', label='RBF Model')
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)
ax.xaxis.set_minor_locator(months)
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
fig.autofmt_xdate()
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Support Vector Regression')
plt.legend()
plt.show()

