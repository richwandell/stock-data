from flask import Flask, render_template, Response
import json, hashlib
from utils import AlphaVantage, Db
import pandas as pd

app = Flask(__name__)


def get_alpha_vantage_creds():
    with open("creds.json") as f:
        credentials = json.loads(f.read())
        return credentials


def get_config():
    with open("config.json") as f:
        config = json.loads(f.read())
        return config


@app.route("/")
def index():
    return render_template('index.jinja2')


@app.route("/config.json")
def config():
    resp = Response(json.dumps(get_config()))
    resp.headers['Content-Type'] = 'Application/javascript'
    return resp


@app.route("/portfolios/get/<portfolio>", methods=['POST'])
def get_all_portfolios(portfolio):
    db = Db()
    if portfolio == "S&P 500":
        snp = pd.read_csv("cache/s&p500_companies.csv")
        port = {
            "symbols": snp['Symbol'].as_matrix().tolist(),
            "name": "S&P 500"
        }
    else:
        config = get_config()
        port = []
        for p in config["portfolios"]:
            if p["name"] == portfolio:
                port = p
                break

    if len(port) == 0:
        snp = pd.read_csv("cache/s&p500_companies.csv")
        port = {
            "name": portfolio,
            "symbols": list(snp[snp['GICS Sector'] == portfolio]['Symbol'])
        }

    symbol_string = "_".join(port["symbols"])
    portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()

    return_data = {}
    try:
        monthly = db.get_monthly_portfolio_stats(portfolio_key + "_monthly")
        return_data["assets"] = json.loads(monthly)
    except:
        pass
    try:
        efficient = db.get_monthly_portfolio_stats(portfolio_key + "_efficient")
        return_data["efficient"] = json.loads(efficient)
    except:
        pass

    data = json.dumps(return_data)

    resp = Response(data)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route("/portfolios/symbols/snp500", methods=['POST'])
def get_snp_symbols():
    snp = pd.read_csv("cache/s&p500_companies.csv")
    portfolio = {
        "symbols": snp['Symbol'].as_matrix().tolist(),
        "name": "S&P 500"
    }
    data = json.dumps(portfolio)
    resp = Response(data)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route("/portfolios/get/snp500", methods=['POST'])
def get_snp_portfolios():
    snp = pd.read_csv("cache/s&p500_companies.csv")
    portfolio = {
        "symbols": snp['Symbol'].as_matrix().tolist(),
        "name": "S&P 500"
    }
    db = Db()
    symbol_string = "_".join(portfolio["symbols"])
    portfolio_key = hashlib.md5(symbol_string.encode("utf8")).hexdigest()

    return_data = {}
    try:
        monthly = db.get_monthly_portfolio_stats(portfolio_key + "_monthly")
        return_data["assets"] = json.loads(monthly)
    except:
        pass
    try:
        efficient = db.get_monthly_portfolio_stats(portfolio_key + "_efficient")
        return_data["efficient"] = json.loads(efficient)
    except:
        pass

    data = json.dumps(return_data)

    resp = Response(data)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route("/portfolios/get/snpPortfolios", methods=['POST'])
def get_all_snp_portfolios():
    snp = pd.read_csv("cache/s&p500_companies.csv")
    sub_industries = snp['GICS Sector'].unique()

    portfolios = []
    for ind in sub_industries:
        portfolio = {
            "name": ind,
            "symbols": list(snp[snp['GICS Sector'] == ind]['Symbol'])
        }
        portfolios.append(portfolio)

    data = json.dumps(portfolios)

    resp = Response(data)
    resp.headers['Content-Type'] = 'application/json'
    return resp
