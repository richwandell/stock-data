from auto_trading import AutoTrader
import pandas as pd
from datetime import datetime
from datetime import timedelta


class MACDAutoTrader(AutoTrader):

    def get_trades(self, time_delta=timedelta(days=365))->pd.DataFrame:
        df = self.df.copy()
        df[self.date_time] = pd.to_datetime(df[self.date_time])

        df = df[df[self.date_time] > datetime.now() - time_delta]
        df = df.reset_index()
        days_12 = df[self.close].ewm(span=12).mean()
        days_12 = days_12.reset_index()
        days_26 = df[self.close].ewm(span=26).mean()
        days_26 = days_26.reset_index()

        macd_line = pd.DataFrame(days_12[self.close] - days_26[self.close], columns=[self.close])
        macd_line.index = df[self.date_time]
        macd_line = macd_line.reset_index()

        signals = pd.DataFrame(df[self.date_time], columns=[self.date_time, 'signal'])
        signals['signal'] = 0
        for i, hist in enumerate(macd_line[self.close]):
            if i > 0:
                # buy signal
                if macd_line[self.close].loc[i - 1] < 0 < hist:
                    signals.set_value(i, 'signal', 1)
                elif macd_line[self.close].loc[i - 1] > 0 > hist:
                    signals.set_value(i, 'signal', 2)
        return signals.set_index(self.date_time)
