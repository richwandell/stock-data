import os
import sys
from multiprocessing import Queue
from multiprocessing.pool import Pool

from utils.kalman_utils import pool_init, run_kalman, DEAD

sys.path.append("..")
from utils.Db import Db
import pandas as pd
import matplotlib.dates as mdates
import numpy as np

if __name__ == '__main__':
    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    days = mdates.DayLocator()
    yearsFmt = mdates.DateFormatter('%Y-%')

    db = Db("../cache")

    df = db.get_symbols_as_dataframe(['AAPL'])
    df['date_time'] = pd.to_datetime(df['date_time'])
    kalman_data = df[['unix_time', 'adjusted_close', 'date_time']].as_matrix()

    queue = Queue()
    pool = Pool(initializer=pool_init, initargs=(queue,), processes=os.cpu_count())

    future = 30
    pool_args = []
    for i in range(1, len(kalman_data)):
        if i % future == 0:
            pool_args.append((i, future, kalman_data))

    pool.map(run_kalman, pool_args)

    returned = 0
    results = []
    while True:
        out = queue.get(True)
        if out != DEAD:
            results.append(list(out))
        returned += 1
        if returned == len(pool_args):
            break
    results = sorted(results, key=lambda x: x[0])
    df = pd.DataFrame(results, columns=['row', 'date_time', 'prediction', 'error'])
    print(df)





