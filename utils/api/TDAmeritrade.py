import datetime
import time

import requests

from utils.api.StockPriceAPIClient import StockPriceAPIClient
from utils.db.Db import MySQLDb


class TDAmeritrade(StockPriceAPIClient):

    ENDPOINT = "https://api.tdameritrade.com/v1/marketdata/%s/pricehistory"

    def __init__(self, db: MySQLDb, apikey: str, requests_per_second=2, cache_folder="cache"):
        StockPriceAPIClient.__init__(self, db, cache_folder)
        self.requests_per_second = requests_per_second
        self.apikey = apikey
        self.rps = 0

    def load_symbol(self, symbol):
        if self.rps == self.requests_per_second:
            print("waiting")
            time.sleep(1)
            self.rps = 0

        if not self.db.has_request_today(symbol):
            r = requests.get(
                url=self.ENDPOINT % symbol,
                params={
                    'apikey': self.apikey,
                    "periodType": "year",
                    "frequencyType": "daily",
                    "period": 10
                },
                headers={
                    'Accept': 'application/json'
                }
            )
            try:
                data = r.json()
            except Exception as e:
                print(e)
                return
            if 'candles' not in data:
                print(data)
                return

            records = []
            for date in data['candles']:
                records.append([
                    symbol,
                    int(date['datetime'] / 1000),
                    float(date['low']),
                    float(0.0),
                    float(0.0),
                    float(date['open']),
                    float(0.0),
                    float(date['close']),
                    float(date['high']),
                    float(date['volume'])
                ])
            self.db.insert_symbol_records(records)
            date_string = datetime.datetime.today().strftime(self.date_key)
            today = int(datetime.datetime.strptime(date_string, self.date_key).timestamp())
            self.db.insert_api_request(today, symbol)
            self.rps += 1
