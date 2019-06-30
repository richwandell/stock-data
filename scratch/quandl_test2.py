# import needed modules
import json

import quandl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from utils.db.Db import MySQLDb as Db

from utils.api.Quandl import Quandl

if __name__ == "__main__":
    with open("creds.json") as f:
        credentials = json.loads(f.read())
        quandl_api_key = credentials["quandl"]["apikey"]

    db = Db(
        host=credentials['mysql']['host'],
        user=credentials['mysql']['user'],
        password=credentials['mysql']['password'],
        database=credentials['mysql']['database']
    )

    quandl_api = Quandl(
            db=db,
            apikey=quandl_api_key
        )
    quandl_api.load_symbol('AABA')