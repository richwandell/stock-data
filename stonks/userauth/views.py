from django.contrib.auth import authenticate, login
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stonks.decorators import post_json_not_empty
from stonks.userauth.serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView


@api_view(['GET'])
def get_user(request):
    serializer = UserSerializer(request.user)
    return Response({**serializer.data, **{"logged_in": True}})


@api_view(['POST'])
@post_json_not_empty(['user', 'pass'])
def user_login(request):

    user = authenticate(username=request.data['user'], password=request.data['pass'])
    if user is not None:
        login(request=request, user=user)
        return Response({
            'user': {**UserSerializer(user).data, "logged_in": True}
        })
    else:
        raise Http404()


@csrf_exempt
def graphql_view(request):
    if request.user.is_anonymous:
        raise Http404()
    return GraphQLView.as_view(graphiql=True)(request)
