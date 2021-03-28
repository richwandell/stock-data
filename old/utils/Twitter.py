import os

import requests
from searchtweets import load_credentials, gen_rule_payload, ResultStream
from textblob import TextBlob
from datetime import datetime, timedelta
from utils import Db


class Twitter:

    def __init__(self,
                 db: Db,
                 twitter_handles=None,
                 consumer_key=None,
                 consumer_secret=None,
                 product=None,
                 environment=None):
        os.environ["SEARCHTWEETS_CONSUMER_KEY"] = consumer_key
        os.environ["SEARCHTWEETS_CONSUMER_SECRET"] = consumer_secret
        products = ['fullarchive', '30day']
        os.environ["SEARCHTWEETS_ENDPOINT"] = 'https://api.twitter.com/1.1/tweets/search/'+product+'/'+environment+'.json'
        os.environ["SEARCHTWEETS_ACCOUNT_TYPE"] = 'premium'
        self.db = db
        self.handles = twitter_handles

    def load_symbol(self, symbol):
        if symbol not in self.handles: raise Exception("Missing handle")
        handle = self.handles[symbol]
        premium_search_args = load_credentials()
        today = datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(1, 30):
            delta = timedelta(days=i)
            from_date = today - delta
            if self.db.has_tweets_for_date(symbol, from_date): continue
            to_date = from_date + timedelta(days=1)
            try:
                rule = gen_rule_payload(
                    handle + " lang:en",
                    from_date=from_date.strftime("%Y%m%d%H%M"),
                    to_date=to_date.strftime("%Y%m%d%H%M")
                )
                rs = ResultStream(
                    rule_payload=rule,
                    max_results=100,
                    **premium_search_args
                )

                for tweet in rs.stream():
                    tweet_id = tweet.id
                    created = tweet.created_at_datetime
                    opinion = TextBlob(tweet.all_text)
                    sentiment = opinion.sentiment
                    self.db.save_tweet(symbol, created, tweet_id, sentiment.polarity, sentiment.subjectivity)
            except requests.exceptions.HTTPError as e:
                print(e)
                return



