from .models import DataSource, DataSourceCredential, Portfolio
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


class PortfolioType(DjangoObjectType):

    class Meta:
        model = Portfolio
        fields = ("id", "name", "user")

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


schema = graphene.Schema(query=Query)