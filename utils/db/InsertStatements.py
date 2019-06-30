class MySQLInsertStatements:
    INSERT_SYMBOL_PRICES = """
    insert into symbol_prices values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    on duplicate key update symbol=symbol;
    """
    INSERT_API_REQUEST = """
    insert into api_requests values (%s, %s)
    on duplicate key update symbol=symbol;
    """
    INSERT_MONTHLY_PORTFOLIO_STATS = """
    insert into monthly_portfolio_stats values (%s, %s)
    on duplicate key update portfolio_data=%s;
    """
    INSERT_TWITTER_SENTIMENT = """
    insert into twitter_sentiment values (%s, %s, %s, %s, %s)
    on duplicate key update symbol=symbol;
    """
    INSERT_NEWSAPI_SENTIMENT = """
    insert into newsapi_sentiment values (%s, %s, %s, %s, %s)
    on duplicate key update symbol=symbol;
    """