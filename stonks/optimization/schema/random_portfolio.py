import graphene


class Covariance(graphene.ObjectType):
    data = graphene.List(of_type=list)
    index = graphene.List(of_type=list)
    columns = graphene.List(of_type=list)


class RandomPortfolioType(graphene.Scalar):
    portfolios = graphene.List(of_type=list)
    column_names = graphene.List(of_type=str)
    returns_monthly = graphene.List(of_type=float)
    returns_mean = graphene.List(of_type=float)
    annualized_return = graphene.List(of_type=float)
    covariance = Covariance

    @staticmethod
    def serialize(root):
        return {
            'portfolios': root.args[0],
            'column_names': root.args[1],
            'returns_monthly': root.args[2],
            'returns_mean': root.args[3],
            'annualized_return': root.args[4],
            'covariance': root.args[5],
        }


class RandomMonthlyPortfolioStatsType(graphene.ObjectType):
    portfolio_id = graphene.String()
    portfolio_stats = graphene.Field(RandomPortfolioType)

    def resolve_portfolio_stats(self, info):
        return RandomPortfolioType(
            self.portfolio_stats['portfolios'],
            self.portfolio_stats['column_names'],
            self.portfolio_stats['returns_monthly'],
            self.portfolio_stats['returns_mean'],
            self.portfolio_stats['annualized_return'],
            self.portfolio_stats['covariance'],
        )

    def resolve_portfolio_id(self, info):
        return self.portfolio_id
