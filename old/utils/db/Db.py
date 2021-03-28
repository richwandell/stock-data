import datetime
import json
from typing import Tuple

import mysql.connector
import numpy as np
import pandas as pd

from utils.db.CreateStatements import MySQLCreateStatements
from utils.db.InsertStatements import MySQLInsertStatements
from utils.db.SelectStatements import MySQLSelectStatements
from utils.db.UpdateStatements import MySQLUpdateStatements


class MySQLDb(MySQLCreateStatements, MySQLInsertStatements, MySQLSelectStatements, MySQLUpdateStatements):

    DATE_KEY = '%Y-%m-%d'

    def __init__(self, host: str, user: str, password: str, database: str)->None:
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=database
        )
        cur = self.conn.cursor()
        cur.execute(self.CREATE_SYMBOL_PRICES)
        cur.execute(self.CREATE_API_REQUESTS)
        cur.execute(self.CREATE_MONTHLY_PORTFOLIO_STATS)
        cur.execute(self.CREATE_TWITTER_SENTIMENT)
        cur.execute(self.CREATE_NEWS_API)
        cur.execute("SET sql_mode = '';")
        cur.execute("SET time_zone='+0:00';")

    def close(self):
        self.conn.close()

    def insert_symbol_records(self, records: list)->None:
        cur = self.conn.cursor()
        cur.executemany(self.INSERT_SYMBOL_PRICES, records)
        self.conn.commit()

    def insert_api_request(self, timestamp: int, symbol: str)->None:
        cur = self.conn.cursor()
        cur.execute(self.INSERT_API_REQUEST, [timestamp, symbol])
        self.conn.commit()

    def has_request_today(self, symbol: str) -> bool:
        cur = self.conn.cursor()
        date_string = datetime.datetime.today().strftime(self.DATE_KEY)
        today_timestamp = int(datetime.datetime.strptime(date_string, self.DATE_KEY).timestamp())
        cur.execute(self.SELECT_API_REQUESTS, [today_timestamp, symbol])
        one = cur.fetchone()
        return one is not None

    def get_symbols_ten_year(self, symbols)->Tuple[pd.DataFrame, list]:
        query = self.SELECT_SYMBOLS_WITH_TEN_YEARS % {"symbols": "'" + "','".join(symbols) + "'"}
        cur = self.conn.cursor()
        cur.execute(query)
        all = list([x[0] for x in cur.fetchall()])
        query = self.SELECT_SYMBOL_PRICES_SYMBOLS_TEN_YEAR % {"symbols": "'" + "','".join(all) + "'"}
        return pd.read_sql_query(query, con=self.conn), all

    def get_symbols_as_dataframe(self, symbols)->pd.DataFrame:
        query = self.SELECT_SYMBOL_PRICES_SYMBOLS % {"symbols": "'" + "','".join(symbols) + "'"}
        return pd.read_sql_query(query, con=self.conn)

    def get_monthly_portfolio_stats(self, key):
        cur = self.conn.cursor()
        cur.execute(self.GET_MONTHLY_PORTFOLIO_STATS, [key])
        one = cur.fetchone()
        return one[0]

    def get_average_daily_twitter_sentiment_as_dataframe(self, symbols: list)->pd.DataFrame:
        query = self.SELECT_AVERAGE_DAILY_TWITTER_SENTIMENT % {"symbols": "'" + "','".join(symbols) + "'"}
        return pd.read_sql_query(query, con=self.conn)

    def get_daily_twitter_sentiment_as_dataframe(self, symbols: list)->pd.DataFrame:
        query = self.SELECT_DAILY_TWITTER_SENTIMENT % {"symbols": "'"+"','".join(symbols)+"'"}
        return pd.read_sql_query(query, con=self.conn)

    def get_daily_newsapi_sentiment_as_dataframe(self, symbols: list)->pd.DataFrame:
        query = self.SELECT_DAILY_NEWSAPI_SENTIMENT % {"symbols": "'"+"','".join(symbols)+"'"}
        return pd.read_sql_query(query, con=self.conn)

    def has_tweets_for_date(self, symbol: str, date_time: datetime.datetime)->bool:
        cur = self.conn.cursor(buffered=True)
        cur.execute(self.SELECT_HAS_TWEETS_FOR_DATE, [symbol, str(int(date_time.timestamp()))])
        one = cur.fetchone()
        cur.close()
        return one is not None

    def has_newsapi_articles_for_date(self, symbol: str, date_time: datetime.datetime)->bool:
        cur = self.conn.cursor(buffered=True)
        query = self.SELECT_HAS_NEWSAPI_ARTICLES_FOR_DATE
        cur.execute(query, [symbol, str(int(date_time.timestamp()))])
        one = cur.fetchone()
        cur.close()
        return one is not None

    def save_newsapi_article_sentiment(self, symbol, created: datetime.datetime, article_id: str, polarity: float, subjectivity: float):
        cur = self.conn.cursor()
        cur.execute(self.INSERT_NEWSAPI_SENTIMENT, [symbol, created.timestamp(), article_id, polarity, subjectivity])
        self.conn.commit()

    def save_tweet(self, symbol: str, created: datetime.datetime, tweet_id: int, polarity: float, subjectivity: float):
        cur = self.conn.cursor()
        cur.execute(self.INSERT_TWITTER_SENTIMENT, [symbol, created.timestamp(), tweet_id, polarity, subjectivity])
        self.conn.commit()

    def save_efficient_portfolio_stats(self, key, portfolios: np.ndarray, symbols: list):
        json_string = json.dumps({
            "portfolios": portfolios.tolist(),
            "symbols": symbols
        })
        cur = self.conn.cursor()
        cur.execute(self.INSERT_MONTHLY_PORTFOLIO_STATS, [key, json_string, json_string])
        self.conn.commit()

    def save_monthly_portfolio_stats(self, key, asset_risk, asset_reward, assets):
        json_string = json.dumps({
            "asset_risk": list(asset_risk),
            "asset_reward": list(asset_reward),
            "assets": list(assets)
        })
        cur = self.conn.cursor()
        cur.execute(self.INSERT_MONTHLY_PORTFOLIO_STATS, [key, json_string, json_string])
        self.conn.commit()

    def get_monthly_symbols_as_dataframe(self, symbols)->pd.DataFrame:
        query = self.SELECT_SYMBOLS_WITH_THIS_MONTH_AND_FIVE_YEARS % {"symbols": "'" + "','".join(symbols) + "'"}
        cur = self.conn.cursor()
        cur.execute(query)
        all = list([x[0] for x in cur.fetchall()])
        df = None
        for symbol in all:
            query = self.GET_MONTHLY_SYMBOLS_AS_DATAFRAME % {"symbols": "'" + symbol + "'"}
            tdf = pd.read_sql_query(query, con=self.conn)
            if df is None:
                df = tdf
            else:
                df = df.append(tdf)
        return df









