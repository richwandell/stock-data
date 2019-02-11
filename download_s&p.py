import json, os
import numpy as np
import matplotlib.pyplot as plt
from utils import AlphaVantage, Db
import hashlib, time
import pandas as pd


if __name__ == '__main__':
    with open("creds.json") as f:
        credentials = json.loads(f.read())
        alpha_vantage_apikey = credentials["alphavantage"]["apikey"]

    with open("config.json") as f:
        config = json.loads(f.read())
        alpha_vantage_rpm = config["alphavantage"]["requests_per_minute"]

    snp = pd.read_csv("cache/s&p500_companies.csv")

    alpha_vantage = AlphaVantage(alpha_vantage_apikey, requests_per_minute=alpha_vantage_rpm)
    db = Db()
    portfolio = {
        "symbols": snp['Symbol'].as_matrix().tolist(),
        "name": "S&P 500"
    }

    efficient_frontier, symbols = alpha_vantage.get_efficient_frontier(portfolio)
    symbol_string = "_".join(portfolio["symbols"])
    portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()
    db.save_efficient_portfolio_stats(portfolio_key + "_efficient", efficient_frontier, symbols)
    asset_risk, asset_reward, assets = alpha_vantage.get_monthly_portfolio_stats(portfolio)
    db.save_monthly_portfolio_stats(portfolio_key + "_monthly", asset_risk, asset_reward, assets)

    print("finished")
    # min_volatility = efficient_frontier[:, 0].min()
    # max_sharpe = efficient_frontier[:, 2].max()
    #
    # # use the min, max values to locate and create the two special portfolios
    # min_variance_port = efficient_frontier[efficient_frontier[:, 0] == min_volatility]
    # sharpe_portfolio = efficient_frontier[efficient_frontier[:, 2] == max_sharpe]
    #
    # plt.style.use('seaborn-dark')
    # fig, ax = plt.subplots()
    # plt.title(portfolio['name'])
    # plt.xlabel('Standard Deviation', fontsize=12)
    # plt.ylabel('Mean', fontsize=12)
    # plt.scatter(asset_risk, asset_reward, marker="^")
    # for i, txt in enumerate(assets):
    #     ax.annotate(txt, (asset_risk[i], asset_reward[i]))
    # plt.scatter(x=sharpe_portfolio[:, 0], y=sharpe_portfolio[:, 1], marker="^", s=200, c='blue')
    # plt.scatter(x=min_variance_port[:, 0], y=min_variance_port[:, 1], marker="^", s=200, c='red')
    # plt.plot(efficient_frontier[:, 0], efficient_frontier[:, 1], color='blue')
    # plt.show()




