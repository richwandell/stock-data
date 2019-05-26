import json
import os
import sys

project_root = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(project_root)
from utils import AlphaVantage
from utils.db.Db import MySQLDb as Db
import hashlib

if __name__ == '__main__':
    with open("creds.json") as f:
        credentials = json.loads(f.read())
        alpha_vantage_apikey = credentials["alphavantage"]["apikey"]

    with open("config.json") as f:
        config = json.loads(f.read())
        alpha_vantage_rpm = config["alphavantage"]["requests_per_minute"]

    db = Db(
        host=credentials['mysql']['host'],
        user=credentials['mysql']['user'],
        password=credentials['mysql']['password'],
        database=credentials['mysql']['database']
    )

    alpha_vantage = AlphaVantage(
        db=db,
        apikey=alpha_vantage_apikey,
        requests_per_minute=alpha_vantage_rpm
    )

    for portfolio in config["portfolios"]:
        print("Loading Portfolio: " + str(portfolio['name']))
        symbol_string = "_".join(portfolio["symbols"])
        portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()

        efficient_frontier, symbols = alpha_vantage.get_efficient_frontier(portfolio)
        db.save_efficient_portfolio_stats(portfolio_key + "_efficient", efficient_frontier, symbols)
        asset_risk, asset_reward, assets = alpha_vantage.get_monthly_portfolio_stats(portfolio)
        db.save_monthly_portfolio_stats(portfolio_key + "_monthly", asset_risk, asset_reward, assets)

    print("Finished")


