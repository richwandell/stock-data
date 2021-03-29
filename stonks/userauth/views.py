from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from stonks.decorators import post_json_not_empty
from stonks.userauth.serializers import UserSerializer


@api_view(['GET'])
def get_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@post_json_not_empty(['user', 'pass'])
def login(request):

    user = authenticate(username=request.data['user'], password=request.data['pass'])
    if user is not None:
        return Response({
            'success': True
        })
    else:
        raise Http404()
