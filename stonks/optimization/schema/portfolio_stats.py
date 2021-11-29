import graphene


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
