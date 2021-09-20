from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DataSource, DataSourceCredential, Portfolio, SymbolPrice, ApiRequest, PortfolioSymbol
from django.utils.safestring import mark_safe


class PortfolioSymbolInline(admin.TabularInline):
    model = PortfolioSymbol


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'symbols')

    def symbols(self, obj):
        symbols = PortfolioSymbol.objects.filter(portfolio=obj)
        return mark_safe("<br>".join([f"<a href='/admin/stonksconfig/portfoliosymbol/{x.id}/change/'>{x.symbol}</a>"
                                   for x in symbols]))

    inlines = [
        PortfolioSymbolInline
    ]


admin.site.register(DataSource)
admin.site.register(DataSourceCredential)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(SymbolPrice)
admin.site.register(ApiRequest)
admin.site.register(PortfolioSymbol)
