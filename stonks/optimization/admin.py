from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import OptimizedPortfolio, MonthlyPortfolioStats


class OptimizedPortfolioAdmin(admin.ModelAdmin):
    list_display = ('portfolio_id', 'portfolio')

    def portfolio(self, obj):
        return mark_safe("<br>".join(obj.efficient_portfolio['symbols']))


admin.site.register(OptimizedPortfolio, OptimizedPortfolioAdmin)
admin.site.register(MonthlyPortfolioStats)
