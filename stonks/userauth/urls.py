from django.urls import path
from .views import get_user, login

urlpatterns = [
    path('get-user/', get_user),
    path('login/', login)
]