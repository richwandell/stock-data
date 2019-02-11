from scipy.signal import argrelextrema
import numpy as np
from auto_trading import AutoTrader
import pandas as pd
from datetime import datetime
from datetime import timedelta


class PerfectAutoTrader(AutoTrader):

    def get_trades(self, time_delta=timedelta(days=365))->pd.DataFrame:
        df = self.df.copy()
        df[self.date_time] = pd.to_datetime(df[self.date_time])
        df = df[df[self.date_time] > datetime.now() - time_delta]
        df = df.reset_index()
        scatter_data = df[[self.close, self.date_time]].as_matrix()
        dates = scatter_data[:, 1]

        maxes = argrelextrema(df[self.close].as_matrix(), np.greater, order=5)
        maxes_dates = dates[maxes[0]]
        mins = argrelextrema(df[self.close].as_matrix(), np.less, order=5)
        mins_dates = dates[mins[0]]

        signals = pd.DataFrame(df[self.date_time], columns=[self.date_time, 'signal'])
        signals['signal'] = 0
        signals = signals.set_index(self.date_time)
        for date in mins_dates:
            signals.set_value(date, 'signal', 1)
        for date in maxes_dates:
            signals.set_value(date, 'signal', 2)
        return signals

