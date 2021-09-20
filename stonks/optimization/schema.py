import graphene

from .models import MonthlyPortfolioStats, OptimizedPortfolio


class PortfolioStatType(graphene.Scalar):
    assets = graphene.List(of_type=str)
    asset_risk = graphene.List(of_type=float)
    asset_reward = graphene.List(of_type=float)

    @staticmethod
    def serialize(root):
        return {
            'assets': root.args[0],
            'asset_risk': root.args[1],
            'asset_reward': root.args[2]
        }


class MonthlyPortfolioStatsType(graphene.ObjectType):
    portfolio_id = graphene.String()
    portfolio_stats = graphene.Field(PortfolioStatType)

    def resolve_portfolio_stats(self, info):
        return PortfolioStatType(
            self.portfolio_stats['assets'],
            self.portfolio_stats['asset_risk'],
            self.portfolio_stats['asset_reward']
        )

    def resolve_portfolio_id(self, info):
        return self.portfolio_id


class EfficientPortfolioType(graphene.Scalar):
    symbols = graphene.List(of_type=str)
    portfolios = graphene.List(of_type=list)

    @staticmethod
    def serialize(root):
        return {
            'symbols': root.args[0],
            'portfolios': root.args[1]
        }


class OptimizedPortfolioType(graphene.ObjectType):
    portfolio_id = graphene.String()
    efficient_portfolio = graphene.Field(EfficientPortfolioType)

    def resolve_efficient_portfolio(self, info):
        return EfficientPortfolioType(
            self.efficient_portfolio['symbols'],
            self.efficient_portfolio['portfolios']
        )


class Query(graphene.ObjectType):

    portfolio_stats = graphene.Field(MonthlyPortfolioStatsType, portfolio_id=graphene.String(required=True))
    optimized_portfolios = graphene.Field(OptimizedPortfolioType, portfolio_id=graphene.String(required=True))

    @staticmethod
    def resolve_portfolio_stats(root, info, portfolio_id):
        try:
            return MonthlyPortfolioStats.objects.get(portfolio_id=portfolio_id)
        except MonthlyPortfolioStats.DoesNotExist:
            return None

    @staticmethod
    def resolve_optimized_portfolios(root, info, portfolio_id):
        try:
            return OptimizedPortfolio.objects.get(portfolio_id=portfolio_id)
        except OptimizedPortfolio.DoesNotExist:
            return None
