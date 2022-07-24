from django.db import models
from django.contrib.auth.models import User
import pandas as pd
from datetime import datetime, timedelta

from stocks import querysets
from stocks.indicators import rsi30, rsi70


class Company(models.Model):
    objects: querysets.CompanyQuerySet
    objects = querysets.CompanyQuerySet().as_manager()

    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=15, unique=True)
    active = models.BooleanField(default=True)

    @property
    def main_currency(self):
        if str(self.abbreviation).endswith('.WA'):
            return 'PLN'
        return 'USD'

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def price_rsis(self, period=14):
        prices = Price.objects.far_days_first(
            abbreviation=self.abbreviation).values('closing')
        prices = pd.DataFrame(prices)['closing']
        rsi_70 = rsi70(prices, period)
        rsi_30 = rsi30(prices, period)
        return prices[period:], prices[period:] + rsi_70[period:], prices[period:] - rsi_30[period:]

    def rsi_price_datasets(self, days=100):
        prices, rsi70, rsi30 = self.price_rsis()
        prices, rsi70, rsi30 = prices.tail(
            days), rsi70.tail(days), rsi30.tail(days)
        labels = [(datetime.now() - timedelta(days=idx)).strftime('%Y-%m-%d')
                  for idx in range(days)][::-1]
        data = []
        data.append(
            {'name': 'Price', 'data': list(prices), 'color': '#2469a7'})
        data.append(
            {'name': 'RSI70', 'data': list(rsi70), 'color': '#6ac980'})
        data.append(
            {'name': 'RSI30', 'data': list(rsi30), 'color': '#db3c23'})
        return data, labels


class Price(models.Model):
    objects: querysets.PriceQuerySet
    objects = querysets.PriceQuerySet.as_manager()

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    opening = models.FloatField()
    closing = models.FloatField()

    class Meta:
        unique_together = ('company', 'date')

    def __str__(self) -> str:
        return f'{str(self.company)} {self.date} open: {self.opening:.2f} close: {self.closing:.2f}'


class UserStockTransactions(models.Model):
    objects: querysets.UserStockTransactionsQuerySet
    objects = querysets.UserStockTransactionsQuerySet.as_manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    date = models.DateField(db_index=True)
    buy = models.BooleanField(default=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.user}, buy={self.buy}, {self.company} -> {self.quantity}x{self.price}'


class UserFollowedCompanies(models.Model):
    objects: querysets.UserFollowedCompaniesQuerySet
    objects = querysets.UserFollowedCompaniesQuerySet.as_manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'company')
