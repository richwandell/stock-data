from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DataSource, DataSourceCredential, Portfolio, SymbolPrice, ApiRequest, PortfolioSymbol


class PortfolioSymbolInline(admin.TabularInline):
    model = PortfolioSymbol


class PortfolioAdmin(admin.ModelAdmin):
    inlines = [
        PortfolioSymbolInline
    ]


admin.site.register(DataSource)
admin.site.register(DataSourceCredential)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(SymbolPrice)
admin.site.register(ApiRequest)
admin.site.register(PortfolioSymbol)
