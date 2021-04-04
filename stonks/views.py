# Create your views here.
import os

import django
from django.http import HttpResponse
from django.template import Template, Context

from stonks import settings


def index(request):
    file = os.path.dirname(os.path.abspath(__file__)) + "/frontend/static/frontend/index.html"
    with open(file) as file:

        t = Template(file.read())
        c = Context({'csrf_token': django.middleware.csrf.get_token(request)})

        return HttpResponse(t.render(c))
