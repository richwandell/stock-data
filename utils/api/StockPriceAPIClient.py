from utils.db.Db import Db


class StockPriceAPIClient:

    date_key = '%Y-%m-%d'

    def __init__(self, db: Db, cache_folder="cache"):
        self.cache_folder = cache_folder
        self.db = db

    def load_symbol(self, symbol: str):
        raise NotImplemented
