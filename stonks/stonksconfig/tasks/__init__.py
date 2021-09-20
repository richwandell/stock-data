from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def test_shared():
    import random
    return int(random.random() * 10) * int(random.random() * 10)

from .load_alphavantage_prices import load_alphavantage_prices



