class InsertStatements:
    INSERT_ALPHA_VANTAGE_PRICES = """
        insert or ignore into alpha_vantage_prices values (?,?,?,?,?,?,?,?,?,?)
        """
    INSERT_ALPHA_VANTAGE_API_REQUEST = """
        insert or ignore into alpha_vantage_api_requests values (?,?)
        """
    INSERT_MONTHLY_PORTFOLIO_STATS = """
        insert or ignore into monthly_portfolio_stats values (?, ?);
        """
    INSERT_TWITTER_SENTIMENT = """
        insert or ignore into twitter_sentiment values (?, ?, ?, ?, ?);
    """
    INSERT_NEWSAPI_SENTIMENT = """
        insert or ignore into newsapi_sentiment values (?, ?, ?, ?, ?);
    """


class MySQLInsertStatements(InsertStatements):
    INSERT_ALPHA_VANTAGE_PRICES = """
    insert into alpha_vantage_prices values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    on duplicate key update symbol=symbol;
    """
    INSERT_ALPHA_VANTAGE_API_REQUEST = """
    insert into alpha_vantage_api_requests values (%s, %s)
    on duplicate key update symbol=symbol;
    """
    INSERT_MONTHLY_PORTFOLIO_STATS = """
    insert into monthly_portfolio_stats values (%s, %s)
    on duplicate key update portfolio_key=portfolio_key;
    """
    INSERT_TWITTER_SENTIMENT = """
    insert into twitter_sentiment values (%s, %s, %s, %s, %s)
    on duplicate key update symbol=symbol;
    """
    INSERT_NEWSAPI_SENTIMENT = """
    insert into newsapi_sentiment values (%s, %s, %s, %s, %s)
    on duplicate key update symbol=symbol;
    """