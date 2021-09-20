import logging
import os
import datetime
import time
from typing import List

import requests

from celery import shared_task
from ..models import DataSource, DataSourceCredential, PortfolioSymbol, ApiRequest, SymbolPrice
from redis import Redis
from redis.lock import LockError


class APIRateLimitException(Exception):
    pass


class AlphaVantage:
    ENDPOINT = 'https://www.alphavantage.co/query'
    ERROR_TEXT = "Error Message"
    API_FUNCTION = 'TIME_SERIES_DAILY_ADJUSTED'
    TIME_SERIES_KEY = 'Time Series (Daily)'
    RL_LIST = 'load_symbols_alphavantage_rate_limit_list'

    def __init__(self, cred: DataSourceCredential):
        self.cred = cred
        self.redis = Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT')
        )

    def has_request_today(self, symbol: str):
        today = datetime.datetime.today()
        daystart = datetime.datetime(year=today.year, month=today.month,
                            day=today.day, hour=0, second=0)
        now: float = int(daystart.timestamp())
        request = ApiRequest.objects.filter(symbol__exact=symbol, request_date__gte=now,
                                            dstype=self.cred.datasource.dstype) \
            .count()
        return request > 0

    def add_request_today(self, symbol: str):
        now: float = int(datetime.datetime.now().timestamp())
        try:
            ApiRequest(request_date=now, symbol=symbol, dstype=self.cred.datasource.dstype).save()
        except Exception as e:
            logging.error(e)

    def create_records(self, symbol: str, data):
        combined = data[self.TIME_SERIES_KEY]
        records = []
        for date in combined:
            records.append(SymbolPrice(
                symbol=symbol,
                date_time=datetime.datetime.strptime(date, '%Y-%m-%d'),
                low=float(combined[date]['3. low']),
                dividend_amount=float(combined[date]['7. dividend amount']),
                adjusted_close=float(combined[date]['5. adjusted close']),
                open=float(combined[date]['1. open']),
                split_coefficient=float(combined[date]['8. split coefficient']),
                close=float(combined[date]['4. close']),
                high=float(combined[date]['2. high']),
                volume=float(combined[date]['6. volume'])
            ))
        try:
            SymbolPrice.objects.bulk_create(records, ignore_conflicts=True)
        except Exception as e:
            logging.error(e)

    def load_symbols(self, symbols_to_load: List[str]):
        try:
            with self.redis.lock("load_symbols_alphavantage_lock", blocking_timeout=30):
                self.redis.delete(self.RL_LIST)

                for symbol in symbols_to_load:
                    if self.has_request_today(symbol):
                        continue
                    time_list = self.redis.lrange(self.RL_LIST, 0, 4)
                    now: float = int(datetime.datetime.now().timestamp())
                    if len(time_list) == 5:
                        oldest_ok = datetime.datetime.fromtimestamp(now) - datetime.timedelta(minutes=1)
                        oldest = datetime.datetime.fromtimestamp(int(time_list[0]))
                        if oldest >= oldest_ok:
                            diff = oldest - oldest_ok
                            time.sleep(diff.seconds)
                            now: float = int(datetime.datetime.now().timestamp())
                        self.redis.lpop(self.RL_LIST)
                        self.redis.rpush(self.RL_LIST, now)
                    else:
                        self.redis.rpush(self.RL_LIST, now)

                    r = requests.get(url=self.ENDPOINT, params={
                        'apikey': self.cred.api_key,
                        'function': self.API_FUNCTION,
                        'symbol': symbol,
                        'outputsize': 'full'
                    })
                    self.add_request_today(symbol)
                    try:
                        data = r.json()
                        if self.TIME_SERIES_KEY in data:
                            self.create_records(symbol, data)
                        elif "Note" in data:
                            if "API call frequency" in data["Note"]:
                                raise APIRateLimitException
                        elif self.ERROR_TEXT in data:
                            logging.error("Missing Time Series for: " + symbol)
                            logging.error(data)
                    except Exception as e:
                        logging.error(e)
        except LockError as e:
            logging.error(e)


@shared_task
def load_alphavantage_prices():

    sources_creds = DataSourceCredential.objects.select_related('user')\
        .filter(datasource__dstype__in=[DataSource.Sources.ALPHAVANTAGE])

    for cred in sources_creds:
        symbols_to_load = PortfolioSymbol.objects.select_related('portfolio__user') \
            .filter(portfolio__user=cred.user)
        av = AlphaVantage(cred)
        av.load_symbols(list([x.symbol.strip() for x in symbols_to_load]))

