from flask import Flask, render_template, Response, g
import json, hashlib
from utils import AlphaVantage
from utils.db.Db import Db, SQLLiteDb, MySQLDb
import pandas as pd

app = Flask(__name__)


def get_db()->Db:
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'database'):
        config = get_config()
        if config['database'] == "mysql":
            creds = get_creds()
            g.database = MySQLDb(
                host=creds['mysql']['host'],
                user=creds['mysql']['user'],
                password=creds['mysql']['password'],
                database=creds['mysql']['database']
            )
        elif config['database'] == 'sqlite':
            g.database = SQLLiteDb()
    return g.database


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'database'):
        g.database.close()


def get_alpha_vantage_creds():
    with open("creds.json") as f:
        credentials = json.loads(f.read())
        return credentials


def get_config():
    with open("config.json") as f:
        config = json.loads(f.read())
        return config


def get_creds():
    with open("creds.json") as f:
        creds = json.loads(f.read())
        return creds


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
    db = get_db()
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
    db = get_db()
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


@app.route("/stocks/get/<symbol>", methods=['POST'])
def get_stocks_symbol(symbol: str):
    db = get_db()
    ten_years = db.get_symbols_ten_year([symbol])[0]
    ten_years['unix_time'] = ten_years['unix_time'] * 1000
    ten_years_ohlc = ten_years[['unix_time', 'open', 'high', 'low', 'close']].as_matrix()
    ten_years_volume = ten_years[['unix_time', 'volume']].as_matrix()
    data = json.dumps({
        'ohlc': ten_years_ohlc.tolist(),
        'volume': ten_years_volume.tolist()
    })
    resp = Response(data)
    resp.headers['Content-Type'] = 'application/json'
    return resp
