import json, os
import numpy as np
import matplotlib.pyplot as plt
from utils import AlphaVantage


if __name__ == '__main__':
    with open("creds.json") as f:
        credentials = json.loads(f.read())

    with open("config.json") as f:
        config = json.loads(f.read())

    apikey = credentials["alphavantage"]["apikey"]
    rpm = config["alphavantage"]["requests_per_minute"]
    alpha_vantage = AlphaVantage(apikey, requests_per_minute=rpm)

    for portfolio in config["portfolios"]:

        risk, reward, portfolio_risk, portfolio_reward = alpha_vantage.get_monthly_portfolio_stats(portfolio)
        portfolios, *other = alpha_vantage.get_random_portfolios(portfolio)
        plt.title(portfolio['name'])
        plt.xlabel('Standard Deviation', fontsize=12)
        plt.ylabel('Mean', fontsize=12)
        plt.scatter(risk, reward)
        plt.scatter(portfolios[:, -2], portfolios[:, -1])
        plt.scatter([portfolio_risk], [portfolio_reward])
        plt.show()



