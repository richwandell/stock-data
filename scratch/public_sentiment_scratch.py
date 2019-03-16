import os
import sys


sys.path.append("..")
from utils import Db
import pandas as pd
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from ta import add_all_ta_features


db = Db("../cache")
df = db.get_symbols_as_dataframe(['AAPL'])
df['date_time'] = pd.to_datetime(df['date_time'])

tdf = db.get_daily_twitter_sentiment_as_dataframe(['AAPL'])
tdf['date_time'] = pd.to_datetime(tdf['date_time'])
tdf = tdf.set_index('date_time')
avgt = tdf.resample(rule='D', how='mean')
stdt = tdf.resample(rule='D', how=np.std)

ndf = db.get_daily_newsapi_sentiment_as_dataframe(['AAPL'])
ndf['date_time'] = pd.to_datetime(ndf['date_time'])
ndf = ndf.set_index('date_time')
avgn = ndf.resample(rule='D', how='mean')
stdn = ndf.resample(rule='D', how=np.std)

joined = df.set_index('date_time')
joined = joined.join(avgt, how='inner', rsuffix='_avgt')
joined = joined.join(stdt, how='inner', rsuffix='_stdt')
joined = joined.join(avgn, how='inner', rsuffix='_avgn')
joined = joined.join(stdn, how='inner', rsuffix='_stdn')


corr = joined.corr()
print(joined)

