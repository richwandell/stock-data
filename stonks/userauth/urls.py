from django.urls import path
from .views import get_user, user_login

urlpatterns = [
    path('get-user/', get_user),
    path('login/', user_login)
]