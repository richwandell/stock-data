from django.db import models


class OptimizedPortfolio(models.Model):
    portfolio_id = models.CharField(max_length=200, db_index=True)
    efficient_portfolio = models.JSONField()

    def __str__(self):
        return self.portfolio_id


class MonthlyPortfolioStats(models.Model):
    portfolio_id = models.CharField(max_length=200, db_index=True)
    portfolio_stats = models.JSONField()

    def __str__(self):
        return self.portfolio_id
