class CreateStatements:
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

    CREATE_TWITTER_SENTIMENT = """
    CREATE TABLE if not exists twitter_sentiment
    (
        symbol text,
        date_time int,
        tweet_id int,
        polarity real,
        subjectivity real
    );
    """
    CREATE_TWITTER_SENTIMENT_INDEX = """
        CREATE UNIQUE INDEX IF NOT EXISTS twitter_sentiment_symbol_tweetid_uindex ON twitter_sentiment (symbol, date_time, tweet_id);
        """
    CREATE_NEWS_API = """
    create table if not exists newsapi_sentiment
    (
        symbol text,
        date_time int,
        article_id int,
        polarity real,
        subjectivity real
    );
    """
    CREATE_NEWS_API_INDEX = """
    create unique index if not exists newsapi_sentiment_symbol_articleid_uindex
        on newsapi_sentiment (symbol, date_time, article_id);
    """


class MySQLCreateStatements(CreateStatements):
    CREATE_ALPHA_VANTAGE_PRICES = """
    CREATE TABLE if not exists `alpha_vantage_prices` (
      `symbol` varchar(50) NOT NULL,
      `date_time` int(10) NOT NULL,
      `low` decimal(13,4) NOT NULL,
      `divident_amount` decimal(13,4) NOT NULL,
      `adjusted_close` decimal(13,4) NOT NULL,
      `open` decimal(13,4) NOT NULL,
      `split_coefficient` decimal(13,4) NOT NULL,
      `close` decimal(13,4) NOT NULL,
      `high` decimal(13,4) NOT NULL,
      `volume` bigint(20) NOT NULL,
      PRIMARY KEY (`symbol`,`date_time`,`adjusted_close`),
      UNIQUE KEY `alpha_vantage_prices_symbol_date_time_uindex` (`symbol`,`date_time`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
    CREATE_ALPHA_VANTAGE_API_REQUESTS = """
    CREATE TABLE if not exists `alpha_vantage_api_requests` (
      `request_date` int(10) NOT NULL,
      `symbol` varchar(50) NOT NULL,
      PRIMARY KEY (`request_date`,`symbol`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
    CREATE_MONTHLY_PORTFOLIO_STATS = """
    CREATE TABLE if not exists `monthly_portfolio_stats` (
      `portfolio_key` varchar(200) NOT NULL,
      `portfolio_data` json NOT NULL,
      PRIMARY KEY (`portfolio_key`),
      UNIQUE KEY `portfolio_key_UNIQUE` (`portfolio_key`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
    CREATE_TWITTER_SENTIMENT = """
    CREATE TABLE if not exists `twitter_sentiment` (
      `symbol` varchar(50) NOT NULL,
      `date_time` int(10) NOT NULL,
      `tweet_id` bigint(20) NOT NULL,
      `polarity` double NOT NULL,
      `subjectivity` double NOT NULL,
      PRIMARY KEY (`symbol`,`date_time`,`tweet_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
    CREATE_NEWS_API = """
    CREATE TABLE if not exists `newsapi_sentiment` (
      `symbol` varchar(50) NOT NULL,
      `date_time` int(10) NOT NULL,
      `article_id` varchar(64) NOT NULL,
      `polarity` double NOT NULL,
      `subjectivity` double NOT NULL,
      PRIMARY KEY (`symbol`,`date_time`,`article_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """