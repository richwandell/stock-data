from django.utils.translation import gettext_lazy as _
from django.db import models


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


class DataSourceCredentials(models.Model):
    api_key = models.CharField(max_length=500)
    datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE)

    def __str__(self):
        return self.datasource.dstype