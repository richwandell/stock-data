from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DataSource, DataSourceCredentials, Portfolio

admin.site.register(DataSource)
admin.site.register(DataSourceCredentials)
admin.site.register(Portfolio)
