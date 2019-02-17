import numpy as np
import pandas as pd
from datetime import timedelta


class AutoTrader:

    def __init__(
            self,
            df: pd.DataFrame,
            date_time="date_time",
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume"
    ):
        self.df = df
        self.date_time = date_time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.columns = ['volume_adi', 'volume_obv', 'volume_obvm', 'volume_cmf', 'volume_fi', 'volume_em', 'volume_vpt',
                        'volume_nvi', 'volatility_atr', 'volatility_bbh', 'volatility_bbl', 'volatility_bbm',
                        'volatility_bbhi',
                        'volatility_bbli', 'volatility_kcc', 'volatility_kch', 'volatility_kcl', 'volatility_kchi',
                        'volatility_kcli', 'volatility_dch', 'volatility_dcl', 'volatility_dchi', 'volatility_dcli',
                        'trend_macd',
                        'trend_macd_signal', 'trend_macd_diff', 'trend_ema_fast', 'trend_ema_slow', 'trend_adx',
                        'trend_adx_pos',
                        'trend_adx_neg', 'trend_vortex_ind_pos', 'trend_vortex_ind_neg', 'trend_vortex_diff',
                        'trend_trix',
                        'trend_mass_index', 'trend_cci', 'trend_dpo', 'trend_kst', 'trend_kst_sig', 'trend_kst_diff',
                        'trend_ichimoku_a', 'trend_ichimoku_b', 'trend_visual_ichimoku_a', 'trend_visual_ichimoku_b',
                        'trend_aroon_up', 'trend_aroon_down', 'trend_aroon_ind', 'momentum_rsi', 'momentum_mfi',
                        'momentum_tsi',
                        'momentum_uo', 'momentum_stoch', 'momentum_stoch_signal', 'momentum_wr', 'momentum_ao',
                        'make_a_trade']

    def get_trades(self, time_delta=timedelta(days=365)) -> pd.DataFrame:
        raise Exception("Not Implemented")


def calculate_profit(df: pd.DataFrame, trades: pd.DataFrame, close='close', date_time='date_time', start_money=1000)->tuple:
    df[date_time] = pd.to_datetime(df[date_time])
    current_money = start_money
    current_shares = 0
    for i, trade in enumerate(trades['signal']):
        if trade == 1:
            date = trades.index[i]
            price = float(df[close][df[date_time] == date])
            buying = np.floor(current_money / price)
            current_shares += buying
            current_money -= buying * price
        elif trade == 2:
            date = trades.index[i]
            price = float(df[close][df[date_time] == date])
            current_money += price * current_shares
            current_shares = 0
    ending_price = float(df[close].loc[df.index[-1]])
    current_money += ending_price * current_shares

    start_date = trades.index[0]
    start_price = float(df[close][df[date_time] == start_date])
    bnh_shares = np.floor(start_money / start_price)
    bnh_start_money = start_money - (bnh_shares * start_price)
    bnh_end_money = ending_price * bnh_shares + bnh_start_money

    return current_money, bnh_end_money
