import time

from utils.Exceptions import APIRateLimitException
from utils.api.StockPriceAPIClient import StockPriceAPIClient
from utils.db.Db import Db
import requests


class Quandl(StockPriceAPIClient):

    ENDPOINT = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.json'

    def __init__(self, db: Db, apikey: str, requests_per_ten_seconds=300, cache_folder="cache"):
        StockPriceAPIClient.__init__(self, db, cache_folder)
        self.requests_per_ten_seconds = requests_per_ten_seconds
        self.apikey = apikey
        self.rps = 0

    def load_symbol(self, symbol):
        if self.rps == self.requests_per_ten_seconds:
            print("waiting")
            time.sleep(10)
            self.rps = 0

        if not self.db.has_request_today(symbol):
            r = requests.get(url=self.ENDPOINT % symbol, params={
                'api_key': self.apikey,
            })
            try:
                data = r.json()
            except Exception as e:
                print(e)
                return
            if "quandl_error" in data:
                print(data)
                error_code = data["quandl_error"]["code"]
                if error_code == "QELx02":
                    raise APIRateLimitException
            else:
                print(data)
            self.rps += 1