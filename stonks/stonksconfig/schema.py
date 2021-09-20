import hashlib

from .models import DataSource, DataSourceCredential, Portfolio, PortfolioSymbol
import graphene
from graphene_django import DjangoObjectType


class DataSourceType(DjangoObjectType):

    class Meta:
        model = DataSource
        fields = ("id", "dstype")


class DataSourceCredentialsType(DjangoObjectType):

    class Meta:
        model = DataSourceCredential
        fields = ("id", "api_key", "datasource")


class PortfolioSymbolType(DjangoObjectType):

    class Meta:
        model = PortfolioSymbol
        fields = ("id", "symbol", "portfolio")


class PortfolioIdType(graphene.Scalar):

    @staticmethod
    def serialize(root):
        symbol_string = "_".join(sorted(root.args[0]))
        return hashlib.md5(symbol_string.encode("utf8")).hexdigest()


class PortfolioType(DjangoObjectType):
    portfolio_id = graphene.Field(PortfolioIdType)

    class Meta:
        model = Portfolio
        fields = ("id", "name", "user", "symbols")

    @staticmethod
    def resolve_portfolio_id(root, info):
        s = list([x.symbol for x in root.symbols.all()])
        return PortfolioIdType(s)


class Query(graphene.ObjectType):

    all_credentials = graphene.Field(DataSourceCredentialsType, name=graphene.String(required=True))
    all_portfolios = graphene.List(PortfolioType)

    @staticmethod
    def resolve_all_credentials(root, info, name):
        try:
            return DataSourceCredential.objects.get(datasource__dstype=name, user=info.context.user)
        except DataSourceCredential.DoesNotExist:
            return None

    @staticmethod
    def resolve_all_portfolios(root, info):
        try:
            return Portfolio.objects.filter(user=info.context.user).all()
        except Portfolio.DoesNotExist:
            return None


