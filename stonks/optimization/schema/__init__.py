import graphene

from .optimized_portfolio import OptimizedPortfolioType
from .portfolio_stats import MonthlyPortfolioStatsType
from .random_portfolio import RandomMonthlyPortfolioStatsType
from ..models import MonthlyPortfolioStats, OptimizedPortfolio


class Query(graphene.ObjectType):

    portfolio_stats = graphene.Field(MonthlyPortfolioStatsType, portfolio_id=graphene.String(required=True))
    random_portfolios = graphene.Field(RandomMonthlyPortfolioStatsType, portfolio_id=graphene.String(required=True))
    optimized_portfolios = graphene.Field(OptimizedPortfolioType, portfolio_id=graphene.String(required=True))

    @staticmethod
    def resolve_portfolio_stats(root, info, portfolio_id):
        try:
            return MonthlyPortfolioStats.objects.get(portfolio_id=portfolio_id)
        except MonthlyPortfolioStats.DoesNotExist:
            return None

    @staticmethod
    def resolve_random_portfolios(root, info, portfolio_id):
        try:
            return MonthlyPortfolioStats.objects.get(portfolio_id=portfolio_id + "_random")
        except MonthlyPortfolioStats.DoesNotExist:
            return None

    @staticmethod
    def resolve_optimized_portfolios(root, info, portfolio_id):
        try:
            return OptimizedPortfolio.objects.get(portfolio_id=portfolio_id)
        except OptimizedPortfolio.DoesNotExist:
            return None
