import requests
from django.core.cache import cache
import functools


class ExchangeCurrency():
    URL = 'https://api.exchangerate-api.com/v4/latest/USD'

    def __init__(self):
        self.data = requests.get(self.URL).json()
        self.currencies = self.data['rates']

    def convert(self, from_currency, to_currency, amount):
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]
        amount = round(amount * self.currencies[to_currency], 4)
        return amount


def get_exchange_rate(from_currency, to_currency):
    exchange = ExchangeCurrency()
    return exchange.convert(
        amount=1, from_currency=from_currency, to_currency=to_currency)


def get_or_set_cached_exchange_rate(from_currency, to_currency):
    key = from_currency+to_currency
    return cache.get_or_set(key, functools.partial(
        get_exchange_rate, from_currency, to_currency), timeout=60*60)
