import sqlite3, datetime, json
import pandas as pd
import numpy as np
from typing import Tuple

from utils.db.CreateStatements import CreateStatements
from utils.db.InsertStatements import InsertStatements
from utils.db.SelectStatements import SelectStatements
from utils.db.UpdateStatements import UpdateStatements
from utils.db.json_functions import json_extract


class Db(CreateStatements, InsertStatements, SelectStatements, UpdateStatements):
    DATE_KEY = '%Y-%m-%d'

    def __init__(self, cache_folder="cache")->None:
        self.conn = sqlite3.connect("%s/cache.sqlite3" % cache_folder)
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA cache_size = 4096000;")
        self.conn.execute("PRAGMA optimize;")
        self.conn.execute("PRAGMA busy_timeout = 150000;")
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_PRICES)
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_PRICES_INDEX)
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_PRICES_INDEX_1)
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_API_REQUESTS)
        self.conn.execute(self.CREATE_MONTHLY_PORTFOLIO_STATS)
        self.conn.execute(self.CREATE_MONTHLY_PORTFOLIO_STATS_INDEX)
        self.conn.execute(self.CREATE_TWITTER_SENTIMENT)
        self.conn.execute(self.CREATE_TWITTER_SENTIMENT_INDEX)
        self.conn.execute(self.CREATE_NEWS_API)
        self.conn.execute(self.CREATE_NEWS_API_INDEX)
        self.conn.create_function("json_extract", 2, json_extract)

    def insert_alpha_vantage_records(self, records: list)->None:
        cur = self.conn.cursor()
        cur.executemany(self.INSERT_ALPHA_VANTAGE_PRICES, records)
        self.conn.commit()

    def insert_alpha_vantage_api_request(self, timestamp: int, symbol: str)->None:
        cur = self.conn.cursor()
        cur.execute(self.INSERT_ALPHA_VANTAGE_API_REQUEST, [timestamp, symbol])
        self.conn.commit()

    def has_request_today(self, symbol: str) -> bool:
        cur = self.conn.cursor()
        date_string = datetime.datetime.today().strftime(self.DATE_KEY)
        today_timestamp = int(datetime.datetime.strptime(date_string, self.DATE_KEY).timestamp())
        cur.execute(self.SELECT_ALPHA_VANTAGE_API_REQUESTS, [today_timestamp, symbol])
        one = cur.fetchone()
        return one is not None

    def get_symbols_ten_year(self, symbols)->Tuple[pd.DataFrame, list]:
        query = self.SELECT_SYMBOLS_WITH_TEN_YEARS % {"symbols": "'" + "','".join(symbols) + "'"}
        cur = self.conn.cursor()
        cur.execute(query)
        all = list([x[0] for x in cur.fetchall()])
        query = self.SELECT_ALPHA_VANTAGE_PRICES_SYMBOLS_TEN_YEAR % {"symbols": "'" + "','".join(all) + "'"}
        return pd.read_sql_query(query, con=self.conn), all

    def get_symbols_as_dataframe(self, symbols)->pd.DataFrame:
        query = self.SELECT_ALPHA_VANTAGE_PRICES_SYMBOLS % {"symbols": "'" + "','".join(symbols) + "'"}
        return pd.read_sql_query(query, con=self.conn)

    def get_monthly_symbols_as_dataframe(self, symbols)->pd.DataFrame:
        query = self.GET_MONTHLY_SYMBOLS_AS_DATAFRAME % {"symbols": "'" + "','".join(symbols) + "'"}
        return pd.read_sql_query(query, con=self.conn)

    def save_monthly_portfolio_stats(self, key, asset_risk, asset_reward, assets):
        json_string = json.dumps({
            "asset_risk": list(asset_risk),
            "asset_reward": list(asset_reward),
            "assets": list(assets)
        })
        cur = self.conn.cursor()
        cur.execute(self.INSERT_MONTHLY_PORTFOLIO_STATS, [key, json_string])
        cur.execute(self.UPDATE_MONTHLY_PORTFOLIO_STATS, [json_string, key])
        self.conn.commit()

    def get_monthly_portfolio_stats(self, key):
        cur = self.conn.cursor()
        cur.execute(self.GET_MONTHLY_PORTFOLIO_STATS, [key])
        one = cur.fetchone()
        return one[0]

    def save_efficient_portfolio_stats(self, key, portfolios: np.ndarray, symbols: list):
        json_string = json.dumps({
            "portfolios": portfolios.tolist(),
            "symbols": symbols
        })
        cur = self.conn.cursor()
        cur.execute(self.INSERT_MONTHLY_PORTFOLIO_STATS, [key, json_string])
        cur.execute(self.UPDATE_MONTHLY_PORTFOLIO_STATS, [json_string, key])
        self.conn.commit()

    def has_tweets_for_date(self, symbol: str, date_time: datetime.datetime)->bool:
        cur = self.conn.cursor()
        cur.execute(self.SELECT_HAS_TWEETS_FOR_DATE, [symbol, int(date_time.timestamp())])
        one = cur.fetchone()
        return one is not None

    def has_newsapi_articles_for_date(self, symbol: str, date_time: datetime.datetime)->bool:
        cur = self.conn.cursor()
        cur.execute(self.SELECT_HAS_NEWSAPI_ARTICLES_FOR_DATE, [symbol, int(date_time.timestamp())])
        one = cur.fetchone()
        return one is not None

    def save_tweet(self, symbol: str, created: datetime.datetime, tweet_id: int, polarity: float, subjectivity: float):
        cur = self.conn.cursor()
        cur.execute(self.INSERT_TWITTER_SENTIMENT, [symbol, created.timestamp(), tweet_id, polarity, subjectivity])
        cur.execute(self.UPDATE_TWITTER_SENTIMENT, [polarity, subjectivity, symbol, tweet_id])
        self.conn.commit()

    def save_newsapi_article_sentiment(self, symbol, created: datetime.datetime, article_id: str, polarity: float, subjectivity: float):
        cur = self.conn.cursor()
        cur.execute(self.INSERT_NEWSAPI_SENTIMENT, [symbol, created.timestamp(), article_id, polarity, subjectivity])
        cur.execute(self.UPDATE_NEWSAPI_SENTIMENT, [polarity, subjectivity, symbol, article_id])
        self.conn.commit()

    def get_average_daily_twitter_sentiment_as_dataframe(self, symbols: list)->pd.DataFrame:
        query = self.SELECT_AVERAGE_DAILY_TWITTER_SENTIMENT % {"symbols": "'" + "','".join(symbols) + "'"}
        return pd.read_sql_query(query, con=self.conn)

    def get_daily_twitter_sentiment_as_dataframe(self, symbols: list)->pd.DataFrame:
        query = self.SELECT_DAILY_TWITTER_SENTIMENT % {"symbols": "'"+"','".join(symbols)+"'"}
        return pd.read_sql_query(query, con=self.conn)

    def get_daily_newsapi_sentiment_as_dataframe(self, symbols: list)->pd.DataFrame:
        query = self.SELECT_DAILY_NEWSAPI_SENTIMENT % {"symbols": "'"+"','".join(symbols)+"'"}
        return pd.read_sql_query(query, con=self.conn)









