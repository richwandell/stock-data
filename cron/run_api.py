import json, os, sys
import numpy as np
import matplotlib.pyplot as plt
project_root = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.path.append(project_root)
from utils import AlphaVantage
from utils.db.Db import MySQLDb as Db
import hashlib, time

from utils.NewsAPI import NewsAPI
from utils.Twitter import Twitter

if __name__ == '__main__':
    with open("creds.json") as f:
        credentials = json.loads(f.read())
        twitter_consumer_key = credentials['twitter']['consumer_key']
        twitter_consumer_secret = credentials['twitter']['consumer_secret']
        twitter_product = credentials['twitter']['product']
        twitter_environment = credentials['twitter']['environment']
        alpha_vantage_apikey = credentials["alphavantage"]["apikey"]
        news_apikey = credentials['newsapi.org']['apikey']

    with open("config.json") as f:
        config = json.loads(f.read())
        twitter_handles = config['twitter_handles']
        alpha_vantage_rpm = config["alphavantage"]["requests_per_minute"]

    db = Db(
        host=credentials['mysql']['host'],
        user=credentials['mysql']['user'],
        password=credentials['mysql']['password'],
        database=credentials['mysql']['database']
    )

    news = NewsAPI(db, news_apikey)
    for handle in twitter_handles.keys():
        news.load_symbol(handle)

    twitter = Twitter(
        db=db,
        twitter_handles=twitter_handles,
        consumer_key=twitter_consumer_key,
        consumer_secret=twitter_consumer_secret,
        product=twitter_product,
        environment=twitter_environment
    )

    for handle in twitter_handles.keys():
        twitter.load_symbol(handle)

    alpha_vantage = AlphaVantage(
        db=db,
        apikey=alpha_vantage_apikey,
        requests_per_minute=alpha_vantage_rpm
    )

    start = time.time()

    for portfolio in config["portfolios"]:
        symbol_string = "_".join(portfolio["symbols"])
        portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()

        efficient_frontier, symbols = alpha_vantage.get_efficient_frontier(portfolio)
        # risk_free_frontier, symbols = alpha_vantage.get_risk_free_frontier(portfolio)
        db.save_efficient_portfolio_stats(portfolio_key + "_efficient", efficient_frontier, symbols)
        asset_risk, asset_reward, assets = alpha_vantage.get_monthly_portfolio_stats(portfolio)
        db.save_monthly_portfolio_stats(portfolio_key + "_monthly", asset_risk, asset_reward, assets)

        portfolios, *others = alpha_vantage.get_random_portfolios(portfolio)

        min_volatility = efficient_frontier[:, 0].min()
        max_sharpe = efficient_frontier[:, 2].max()

        # use the min, max values to locate and create the two special portfolios
        min_variance_port = efficient_frontier[efficient_frontier[:, 0] == min_volatility]
        sharpe_portfolio = efficient_frontier[efficient_frontier[:, 2] == max_sharpe]

        plt.style.use('seaborn-dark')
        fig, ax = plt.subplots()
        plt.title(portfolio['name'])
        plt.xlabel('Standard Deviation', fontsize=12)
        plt.ylabel('Mean', fontsize=12)
        plt.scatter(asset_risk, asset_reward, marker="^")
        for i, txt in enumerate(assets):
            ax.annotate(txt, (asset_risk[i], asset_reward[i]))
        plt.scatter(x=portfolios[:, -3], y=portfolios[:, -2], c=portfolios[:, -1], cmap='RdYlGn', edgecolors='black')
        plt.colorbar()
        plt.scatter(x=sharpe_portfolio[:, 0], y=sharpe_portfolio[:, 1], marker="^", s=200, c='blue')
        plt.scatter(x=min_variance_port[:, 0], y=min_variance_port[:, 1], marker="^", s=200, c='red')
        plt.plot(efficient_frontier[:, 0], efficient_frontier[:, 1], color='blue')
        # plt.plot(risk_free_frontier[:, 0], risk_free_frontier[:, 1], color='green')
        plt.show()
    end = time.time()
    # 31.766854286193848
    # 27.051352739334106
    # 23.095870971679688
    # 22.9417085647583
    # 22.290102243423462
    print(end - start)


