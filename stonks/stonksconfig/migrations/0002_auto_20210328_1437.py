# Generated by Django 3.1.7 on 2021-03-28 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stonksconfig', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datasource',
            name='name',
        ),
        migrations.AddField(
            model_name='datasource',
            name='type',
            field=models.CharField(choices=[('TD_AMERITRADE', 'TD Ameritrade'), ('QUANDL', 'Quandl'), ('SIMFIN', 'Simfin'), ('ALPHAVANTAGE', 'AlphaVantage'), ('NEWS_API_ORG', 'News API.org'), ('TWITTER', 'Twitter')], default='ALPHAVANTAGE', max_length=500),
        ),
    ]