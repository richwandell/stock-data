from .models import DataSource, DataSourceCredentials
import graphene
from graphene_django import DjangoObjectType


class DataSourceType(DjangoObjectType):

    class Meta:
        model = DataSource
        fields = ("id", "dstype")


class DataSourceCredentialsType(DjangoObjectType):

    class Meta:
        model = DataSourceCredentials
        fields = ("id", "api_key", "datasource")


class Query(graphene.ObjectType):

    all_credentials = graphene.Field(DataSourceCredentialsType, name=graphene.String(required=True))

    @staticmethod
    def resolve_all_credentials(root, info, name):
        try:
            return DataSourceCredentials.objects.get(datasource__dstype=name)
        except DataSourceCredentials.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)