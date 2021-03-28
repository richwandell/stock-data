# Create your views here.
from django.http import HttpResponse

from stonks import settings


def index(request):
    file = settings.STATIC_ROOT + "/frontend/index.html"
    with open(file) as file:
        return HttpResponse(file.read())
