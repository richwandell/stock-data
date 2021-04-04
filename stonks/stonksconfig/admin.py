from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DataSource, DataSourceCredential, Portfolio, SymbolPrice, ApiRequest

admin.site.register(DataSource)
admin.site.register(DataSourceCredential)
admin.site.register(Portfolio)
admin.site.register(SymbolPrice)
admin.site.register(ApiRequest)
