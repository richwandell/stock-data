from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User


class DataSource(models.Model):

    class SourceTypes(models.TextChoices):
        TD_AMERITRADE = 'TD_AMERITRADE', _('TD Ameritrade')
        QUANDL = 'QUANDL', _('Quandl')
        SIMFIN = 'SIMFIN', _('Simfin')
        ALPHAVANTAGE = 'ALPHAVANTAGE', _('AlphaVantage')
        NEWS_API_ORG = 'NEWS_API_ORG', _('News API.org')
        TWITTER = 'TWITTER', _('Twitter')

    dstype = models.CharField(max_length=500, choices=SourceTypes.choices, default=SourceTypes.ALPHAVANTAGE)

    def __str__(self):
        return self.dstype


class DataSourceCredential(models.Model):
    api_key = models.CharField(max_length=500)
    datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.datasource.dstype


class Portfolio(models.Model):
    name = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name


class SymbolPrice(models.Model):
    symbol = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    low = models.DecimalField(max_digits=13, decimal_places=4)
    dividend_amount = models.DecimalField(max_digits=13, decimal_places=4)
    adjusted_close = models.DecimalField(max_digits=13, decimal_places=4)
    open = models.DecimalField(max_digits=13, decimal_places=4)
    split_coefficient = models.DecimalField(max_digits=13, decimal_places=4)
    close = models.DecimalField(max_digits=13, decimal_places=4)
    high = models.DecimalField(max_digits=13, decimal_places=4)
    volume = models.BigIntegerField(max_length=20)

    class Meta:
        constraints = [            
            models.UniqueConstraint(fields=['symbol', 'date_time'], name='symbol_prices_symbol_date_time_uindex')
        ]


class ApiRequest(models.Model):
    request_date = models.IntegerField(max_length=10)
    symbol = models.CharField(max_length=50)

    class Meta:
        constraints = [            
            models.UniqueConstraint(fields=['request_date', 'symbol'], name='request_date_symbol_unique')
        ]


