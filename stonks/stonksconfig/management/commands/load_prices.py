from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Runs load_prices from cli'

    def handle(self, *args, **options):
        from ...tasks import load_alphavantage_prices
        load_alphavantage_prices()
