import sqlite3, datetime
import pandas as pd

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
    CREATE_ALPHA_VANTAGE_API_REQUESTS = """
    CREATE TABLE if not exists alpha_vantage_api_requests
    (
        request_date integer,
        symbol text,
        CONSTRAINT alpha_vantage_api_requests_pk PRIMARY KEY (request_date, symbol)
    );
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

    def __init__(self, cache_folder="cache")->None:
        self.conn = sqlite3.connect("%s/cache.sqlite3" % cache_folder)
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_PRICES)
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_PRICES_INDEX)
        self.conn.execute(self.CREATE_ALPHA_VANTAGE_API_REQUESTS)

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







