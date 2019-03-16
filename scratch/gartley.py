from utils.db.Db import Db
import pandas as pd

db = Db("../cache")
df = db.get_symbols_as_dataframe(['AAPL'])
df['date_time'] = pd.to_datetime(df['date_time'])


def add_bullish_gartley(df: pd.DataFrame)->pd.DataFrame:

    return df
