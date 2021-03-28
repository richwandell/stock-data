class SQLiteUpdateStatements:
    UPDATE_MONTHLY_PORTFOLIO_STATS = """
        update monthly_portfolio_stats set portfolio_data = ? where portfolio_key = ?;
        """
    UPDATE_TWITTER_SENTIMENT = """
        update twitter_sentiment set polarity = ?, subjectivity = ? where symbol = ? and tweet_id = ?;
    """
    UPDATE_NEWSAPI_SENTIMENT = """
        update newsapi_sentiment set polarity = ?, subjectivity = ? where symbol = ? and article_id = ?;
    """


class MySQLUpdateStatements:
    UPDATE_MONTHLY_PORTFOLIO_STATS = """
    update monthly_portfolio_stats set portfolio_data = %s where portfolio_key = %s;
    """