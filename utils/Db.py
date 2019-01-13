import sqlite3, datetime, json
import pandas as pd
import numpy as np

class Db:
    DATE_KEY = '%Y-%m-%d'
    CREATE_ALPHA_VANTAGE_PRICES = """
    CREATE TABLE if not exists alpha_vantage_prices
    (
        symbol text NOT NULL,
        date_time integer NOT NULL,
        low real NOT NULL,
        divident_amount real NOT NULL,
        adjusted_close real NOT NULL,
        open real NOT NULL,
        split_coefficient real NOT NULL,
        close real NOT NULL,
        high real NOT NULL,
        volume real NOT NULL
    );
    """
    CREATE_ALPHA_VANTAGE_PRICES_INDEX = """
    CREATE UNIQUE INDEX if not exists alpha_vantage_prices_symbol_date_time_uindex ON alpha_vantage_prices (symbol, date_time DESC);
    """
    CREATE_ALPHA_VANTAGE_PRICES_INDEX_1 = """
    CREATE INDEX if not exists alpha_vantage_prices_symbol_date_time_adjusted_close_index ON alpha_vantage_prices (symbol, date_time, adjusted_close);
    """
    CREATE_ALPHA_VANTAGE_API_REQUESTS = """
    CREATE TABLE if not exists alpha_vantage_api_requests
    (
        request_date integer,
        symbol text,
        CONSTRAINT alpha_vantage_api_requests_pk PRIMARY KEY (request_date, symbol)
    );
    """
    CREATE_MONTHLY_PORTFOLIO_STATS = """
    CREATE TABLE if not exists monthly_portfolio_stats
    (
        portfolio_key text,
        portfolio_data text
    );
    """
    CREATE_MONTHLY_PORTFOLIO_STATS_INDEX = """
    CREATE UNIQUE INDEX IF NOT EXISTS monthly_portfolio_stats_portfolio_key_uindex ON monthly_portfolio_stats (portfolio_key);
    """

    INSERT_ALPHA_VANTAGE_PRICES = """
    insert or ignore into alpha_vantage_prices values (?,?,?,?,?,?,?,?,?,?)
    """
    INSERT_ALPHA_VANTAGE_API_REQUEST = """
    insert or ignore into alpha_vantage_api_requests values (?,?)
    """
    SELECT_ALPHA_VANTAGE_API_REQUESTS = """
    select * from alpha_vantage_api_requests 
    where date(request_date, 'unixepoch') = date(?, 'unixepoch') and symbol = ?
    """
    SELECT_ALPHA_VANTAGE_PRICES_SYMBOLS = """
    select 
        ap.*, 
        cast(strftime('%%m', date_time, 'unixepoch') as int) as month, 
        cast(strftime('%%Y', date_time, 'unixepoch') as int) as year,
        cast(strftime('%%d', date_time, 'unixepoch') as int) as day 
    from alpha_vantage_prices ap
    where symbol in (%(symbols)s)    
    """
    INSERT_MONTHLY_PORTFOLIO_STATS = """
    insert or ignore into monthly_portfolio_stats values (?, ?);
    """
    UPDATE_MONTHLY_PORTFOLIO_STATS = """
    update monthly_portfolio_stats set portfolio_data = ? where portfolio_key = ?;
    """
    GET_MONTHLY_PORTFOLIO_STATS = """
    select portfolio_data from monthly_portfolio_stats where portfolio_key = ?
    """
    GET_MONTHLY_SYMBOLS_AS_DATAFRAME = """
    select 
        strftime('%%Y-%%m', date_time, 'unixepoch') as date_time, 
        symbol, adjusted_close
    from (select date_time, symbol, adjusted_close
         from alpha_vantage_prices ap
         where symbol in (%(symbols)s)
         order by ap.date_time desc) a
    group by symbol, strftime('%%Y-%%m', a.date_time, 'unixepoch')
    """

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








