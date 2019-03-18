class SelectStatements:
    SELECT_AVERAGE_DAILY_TWITTER_SENTIMENT = """
    select
      symbol,
      strftime('%%Y-%%m-%%d', date_time, 'unixepoch') as date_time,
      avg(polarity) as average_polarity,
      avg(subjectivity) as average_subjectivity
    from twitter_sentiment
    where symbol in (%(symbols)s)  
    group by strftime('%%Y-%%m-%%d', date_time, 'unixepoch')
    """
    SELECT_DAILY_TWITTER_SENTIMENT = """
    select
      symbol,
      strftime('%%Y-%%m-%%d', date_time, 'unixepoch') as date_time,
      polarity,
      subjectivity
    from twitter_sentiment
    where symbol in (%(symbols)s)
    """
    SELECT_DAILY_NEWSAPI_SENTIMENT = """
    select
      symbol,
      strftime('%%Y-%%m-%%d', date_time, 'unixepoch') as date_time,
      polarity,
      subjectivity
    from newsapi_sentiment
    where symbol in (%(symbols)s)
    """
    SELECT_HAS_TWEETS_FOR_DATE = """
    select 1 from twitter_sentiment
    where          
        symbol = ? and 
        date(date_time, 'unixepoch') 
        = date(?, 'unixepoch');
    """
    SELECT_HAS_NEWSAPI_ARTICLES_FOR_DATE = """
    select 1 from newsapi_sentiment
    where          
        symbol = ? and 
        date(date_time, 'unixepoch') 
        = date(?, 'unixepoch');
    """
    SELECT_ALPHA_VANTAGE_API_REQUESTS = """
        select * from alpha_vantage_api_requests 
        where date(request_date, 'unixepoch') = date(?, 'unixepoch') and symbol = ?
        """
    SELECT_ALPHA_VANTAGE_PRICES_SYMBOLS = """
        select 
            symbol,
            strftime('%%Y-%%m-%%d', date_time, 'unixepoch') as date_time,
            date_time as unix_time,
            adjusted_close,
            `close`,
            high,
            low,
            `open`,
            volume         
        from alpha_vantage_prices ap
        where symbol in (%(symbols)s)    
        group by symbol, strftime('%%Y-%%m-%%d', date_time, 'unixepoch')
        """
    SELECT_ALPHA_VANTAGE_PRICES_SYMBOLS_TEN_YEAR = """
        select 
            symbol,
            strftime('%%Y-%%m-%%d', date_time, 'unixepoch') as date_time,
            date_time as unix_time,
            adjusted_close,
            `close`,
            high,
            low,
            `open`,
            volume         
        from alpha_vantage_prices ap
        where symbol in (%(symbols)s)    
        group by symbol, strftime('%%Y-%%m-%%d', date_time, 'unixepoch')
    """
    SELECT_SYMBOLS_WITH_TEN_YEARS = """
    select
      distinct symbol
    from alpha_vantage_prices
    where symbol in (%(symbols)s)
    and strftime('%%Y-%%m-%%d', date_time, 'unixepoch') = date('now', '-10 year');
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


class MySQLSelectStatements(SelectStatements):
    SELECT_SYMBOLS_WITH_TEN_YEARS = """
        select
          distinct symbol
        from alpha_vantage_prices
        where symbol in (%(symbols)s)
        and from_unixtime(date_time, '%%Y-%%m-%%d') = curdate() - interval 10 year;;
    """
    SELECT_ALPHA_VANTAGE_PRICES_SYMBOLS_TEN_YEAR = """        
        select
            symbol,
            from_unixtime(date_time, '%%Y-%%m-%%d') as date_time,
            date_time as unix_time,
            adjusted_close,
            `close`,
            high,
            low,
            `open`,
            volume
        from alpha_vantage_prices ap
        where symbol in (%(symbols)s)
        group by symbol, from_unixtime(date_time, '%%Y-%%m-%%d');
    """
    SELECT_HAS_NEWSAPI_ARTICLES_FOR_DATE = """
    select 1 from newsapi_sentiment
    where          
        symbol = %s and 
        date(from_unixtime(date_time))         
        = date(from_unixtime(%s));
    """