from django.urls import path
from .views import get_user

urlpatterns = [
    path('get-user/', get_user)
]