import graphene
from .stonksconfig.schema import Query as ConfigQuery
from .optimization.schema import Query as OptQuery


class Query(ConfigQuery, OptQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)