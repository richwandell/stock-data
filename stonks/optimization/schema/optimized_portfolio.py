import graphene


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