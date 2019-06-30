import hashlib, re

from utils.EfficientFrontier import EfficientFrontier
from utils.db.Db import Db
from utils.portfolio_predict_utils import get_snp_ten_year
import pandas as pd
import numpy as np

if __name__ == "__main__":
    db = Db("../cache")
    snp = pd.read_csv("../cache/s&p500_companies.csv").as_matrix()
    symbols = list(snp[:, 1])

    df = db.get_monthly_symbols_as_dataframe(symbols)
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.set_index('date_time')
    df = df.pivot(columns='symbol')
    df = df.dropna()
    column_names = [x[1] for x in list(df)]

    returns_monthly = df.pct_change()
    returns_mean = returns_monthly.mean()
    annualized_return = (((1.0 + returns_mean) ** 12.0) - 1.0)
    corr = returns_monthly.corr(method='pearson')

    corr = corr.where(np.triu(np.ones(corr.shape), k=1).astype(np.bool))
    corr = corr.unstack().transpose()\
        .sort_values(by='close', ascending=False)\
        .dropna()

    print("done")