# Create your views here.
import django
from django.http import HttpResponse
from django.template import Template, Context

from stonks import settings


def index(request):
    file = settings.STATIC_ROOT + "/frontend/index.html"
    with open(file) as file:

        t = Template(file.read())
        c = Context({'csrf_token': django.middleware.csrf.get_token(request)})

        return HttpResponse(t.render(c))
