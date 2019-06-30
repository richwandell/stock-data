class SQLiteSelectStatements:
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
    SELECT_API_REQUESTS = """
        select * from api_requests 
        where date(request_date, 'unixepoch') = date(?, 'unixepoch') and symbol = ?
        """
    SELECT_SYMBOL_PRICES_SYMBOLS = """
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
        from symbol_prices ap
        where symbol in (%(symbols)s)    
        group by symbol, strftime('%%Y-%%m-%%d', date_time, 'unixepoch')
        """
    SELECT_SYMBOL_PRICES_SYMBOLS_TEN_YEAR = """
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
        from symbol_prices ap
        where symbol in (%(symbols)s)    
        group by symbol, strftime('%%Y-%%m-%%d', date_time, 'unixepoch')
    """
    SELECT_SYMBOLS_WITH_TEN_YEARS = """
    select
      distinct symbol
    from symbol_prices
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
        from (select date_time, symbol, `adjusted_close`
             from symbol_prices ap
             where symbol in (%(symbols)s)
             order by ap.date_time desc) a
        group by symbol, strftime('%%Y-%%m', a.date_time, 'unixepoch')
        """


class MySQLSelectStatements(SQLiteSelectStatements):
    GET_MONTHLY_PORTFOLIO_STATS = """
    select portfolio_data from monthly_portfolio_stats where portfolio_key = %s
    """
    GET_MONTHLY_SYMBOLS_AS_DATAFRAME = """
    select
        concat(
          year(from_unixtime(date_time)),
          '-',
          LPAD(month(from_unixtime(date_time)), 2, '0')
        ) as date_time,
        symbol, adjusted_close
    from
        symbol_prices
    where symbol in (%(symbols)s)
    and date_time in (
        select max(date_time) from symbol_prices
        where symbol in (%(symbols)s)
        group by year(from_unixtime(date_time)), month(from_unixtime(date_time))
    );
    """
    SELECT_API_REQUESTS = """
    select * from api_requests 
    where date(from_unixtime(request_date)) = date(from_unixtime(%s)) and symbol = %s
    """
    SELECT_SYMBOLS_WITH_TEN_YEARS = """
        select
          distinct symbol
        from symbol_prices
        where symbol in (%(symbols)s)
        and date(from_unixtime(date_time)) = curdate() - interval 10 year;
    """
    SELECT_SYMBOLS_WITH_THIS_MONTH = """
        select
          distinct symbol
        from symbol_prices
        where symbol in (%(symbols)s)
        and date(from_unixtime(date_time)) = curdate() - interval 1 month ;
    """
    SELECT_SYMBOLS_WITH_THIS_MONTH_AND_FIVE_YEARS = """
    select distinct symbol
    from
         symbol_prices
    where symbol in (
      select distinct symbol
      from symbol_prices
      where symbol in (%(symbols)s)
      and month(from_unixtime(date_time)) = month(curdate())
      and year(from_unixtime(date_time)) = year(curdate() - interval 5 year)
    )
    and month(from_unixtime(date_time)) = month(curdate() - interval 1 month)
    and year(from_unixtime(date_time)) = year(curdate());
    """
    SELECT_SYMBOL_PRICES_SYMBOLS = """
    select
        symbol,
        CAST(from_unixtime(date_time) as char) as date_time,
        date_time as unix_time,
        adjusted_close,
        `close`,
        high,
        low,
        `open`,
        volume
    from symbol_prices ap
    where symbol in (%(symbols)s)
    group by symbol, date(from_unixtime(date_time));
    """
    SELECT_SYMBOL_PRICES_SYMBOLS_TEN_YEAR = """        
        select
            symbol,
            CAST(from_unixtime(date_time) as char) as date_time,
            date_time as unix_time,
            adjusted_close,
            `close`,
            high,
            low,
            `open`,
            volume
        from symbol_prices ap
        where symbol in (%(symbols)s)
        group by symbol, date(from_unixtime(date_time));
    """
    SELECT_HAS_NEWSAPI_ARTICLES_FOR_DATE = """
    select 1 from newsapi_sentiment
    where          
        symbol = %s and 
        date(from_unixtime(date_time))         
        = date(from_unixtime(%s));
    """
    SELECT_HAS_TWEETS_FOR_DATE = """
    select 1 from twitter_sentiment
    where          
        symbol = %s and 
        date(from_unixtime(date_time)) 
        = date(from_unixtime(%s));
    """
    SELECT_AVERAGE_DAILY_TWITTER_SENTIMENT = """
    select
      symbol,
      date(from_unixtime(date_time)) as date_time,
      avg(polarity) as average_polarity,
      avg(subjectivity) as average_subjectivity
    from twitter_sentiment
    where symbol in (%(symbols)s)
    group by date(from_unixtime(date_time));
    """
    SELECT_DAILY_NEWSAPI_SENTIMENT = """
    select
      symbol,
      date(from_unixtime(date_time)) as date_time,
      polarity,
      subjectivity
    from newsapi_sentiment
    where symbol in (%(symbols)s)
    """
    SELECT_DAILY_TWITTER_SENTIMENT = """
    select
      symbol,
      date(from_unixtime(date_time)) as date_time,
      polarity,
      subjectivity
    from twitter_sentiment
    where symbol in (%(symbols)s)
    """