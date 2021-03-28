from datetime import timedelta, datetime
import requests, hashlib
from textblob import TextBlob
from utils import Db


class NewsAPI:
    EVERYTHING = "https://newsapi.org/v2/everything"

    def __init__(self, db: Db, apikey: str):
        self.apikey = apikey
        self.db = db

    def load_symbol(self, symbol):
        today = datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(1, 365):
            delta = timedelta(days=i)
            from_date = today - delta
            if self.db.has_newsapi_articles_for_date(symbol, from_date): continue
            to_date = from_date + timedelta(days=1)
            try:
                r = requests.get(self.EVERYTHING, {
                    'q': symbol,
                    'apikey': self.apikey,
                    'from': from_date.strftime("%Y-%m-%d"),
                    'to': to_date.strftime("%Y-%m-%d"),
                    'pageSize': 100,
                    'language': 'en'
                })

                data = r.json()

                for article in data['articles']:
                    article_id = str(article['source']['name'])
                    if article['title'] is not None:
                        article_id += article['title']
                    if article['url'] is not None:
                        article_id += article['url']

                    article_id = hashlib.sha256((article_id.encode('utf8'))).hexdigest()
                    text = article['content']
                    if text is None:
                        text = article['description']
                    if text is None:
                        text = article['title']

                    opinion = TextBlob(text)
                    sentiment = opinion.sentiment
                    published = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                    self.db.save_newsapi_article_sentiment(symbol, published, article_id, sentiment.polarity, sentiment.subjectivity)
            except Exception as e:
                print(e)
                return
