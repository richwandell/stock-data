import datetime, csv
import requests, json, time

from utils.Exceptions import APIRateLimitException
from utils.api.StockPriceAPIClient import StockPriceAPIClient
from utils.db.Db import MySQLDb
import pandas as pd


class AlphaVantage(StockPriceAPIClient):

    api_function = 'TIME_SERIES_DAILY_ADJUSTED'
    error_text = "Error Message"
    time_series_key = 'Time Series (Daily)'
    open_key = "1. open"
    closed_key = "4. close"
    ENDPOINT = 'https://www.alphavantage.co/query'

    def __init__(self, db: MySQLDb, apikey: str, requests_per_minute=5, cache_folder="cache"):
        StockPriceAPIClient.__init__(self, db, cache_folder)
        self.requests_per_minute = requests_per_minute
        self.apikey = apikey
        self.rpm = 0

    def load_symbol(self, symbol):
        if self.rpm == self.requests_per_minute:
            print("waiting")
            time.sleep(60)
            self.rpm = 0

        if not self.db.has_request_today(symbol):
            r = requests.get(url=self.ENDPOINT, params={
                'apikey': self.apikey,
                'function': self.api_function,
                'symbol': symbol,
                'outputsize': 'full'
            })
            try:
                data = r.json()
            except Exception as e:
                print(e)
                return

            if self.time_series_key in data:
                combined = data[self.time_series_key]
                record = []
                for date in combined:
                    record.append([
                        symbol,
                        datetime.datetime.strptime(date, '%Y-%m-%d').timestamp(),
                        float(combined[date]['3. low']),
                        float(combined[date]['7. dividend amount']),
                        float(combined[date]['5. adjusted close']),
                        float(combined[date]['1. open']),
                        float(combined[date]['8. split coefficient']),
                        float(combined[date]['4. close']),
                        float(combined[date]['2. high']),
                        float(combined[date]['6. volume'])
                    ])
                self.db.insert_symbol_records(record)
                date_string = datetime.datetime.today().strftime(self.date_key)
                today = int(datetime.datetime.strptime(date_string, self.date_key).timestamp())
                self.db.insert_api_request(today, symbol)
                self.rpm += 1
            elif "Note" in data:
                if "API call frequency" in data["Note"]:
                    raise APIRateLimitException
            elif "Error Message" in data:
                print("Missing Time Series for: " + symbol)
                print(data)
                self.rpm += 1
