import os

import pandas as pd
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs portfolio optimizer'

    def handle(self, *args, **options):
        from stonks.optimization.tasks import optimize_portfolio
        from stonks.stonksconfig.models import Portfolio
        # snp = pd.read_csv(os.getcwd() + "/old/cache/s&p500_companies.csv")
        # sub_industries = snp['GICS Sector'].unique()
        #
        # for ind in sub_industries:
        #     portfolio = list(snp[snp['GICS Sector'] == ind]['Symbol'])
        #     optimize_portfolio(portfolio)
        portfolios = Portfolio.objects.all()
        for portfolio in portfolios:
            p = list([x.symbol for x in portfolio.symbols.all()])
            optimize_portfolio(p)

