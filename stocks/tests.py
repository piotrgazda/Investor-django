
from datetime import date
from django.test import TestCase
from stocks.models import Company, Price, UserFollowedCompanies, UserStockTransactions
from stocks.indicators import summarize_price

from django.contrib.auth.models import User
import pandas as pd

from authentication.registration import register_user
import itertools
# Create your tests here.


class QuerySetsTest(TestCase):
    def setUp(self):
        self.user = register_user('username', 'password')
        self.create_companies()
        self.create_prices()
        self.create_follows()
        self.create_transactions()

    def create_companies(self):
        self.a = Company.objects.create(
            name='A', abbreviation='A')
        self.b = Company.objects.create(
            name='B', abbreviation='B')
        self.c = Company.objects.create(
            name='C', abbreviation='C', active=False)

    def create_prices(self):
        dates = iter([date(year=2022, month=7, day=day)
                     for day in range(1, 30)])
        prices = itertools.chain.from_iterable(
            itertools.repeat(x, 2) for x in range(1, 30))
        # prices for A, from 1 to 5
        for count in range(4):
            Price.objects.create(
                company=self.a, date=next(dates),  opening=next(prices), closing=next(prices))
        # prices for B, from 6 to 10
        for count in range(4):
            Price.objects.create(
                company=self.b, date=next(dates),  opening=next(prices), closing=next(prices))
        # prices for C, not active, from 11 to 15
        for count in range(4):
            Price.objects.create(
                company=self.b, date=next(dates), opening=next(prices), closing=next(prices))

    def create_follows(self):
        UserFollowedCompanies.objects.create(user=self.user, company=self.a)
        UserFollowedCompanies.objects.create(user=self.user, company=self.b)

    def create_transactions(self):
        date1, date2, date3, date4, date5 = [
            date(year=2022, month=7, day=i) for i in [1, 4, 5, 9, 17]]
        self.transactions = []
        # 2+10+5
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.a, date=date1, quantity=2, price=1))  # spent 2
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.a, date=date2, quantity=5, price=2))  # spent 10
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.a, date=date3, quantity=3, price=3, buy=False))  # earned 9
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.a, date=date4, quantity=1, price=5))  # spent 5
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.a, date=date5, quantity=2, price=4, buy=False))  # earned 8

        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.b, date=date1, quantity=1, price=1))  # spent 1
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.b, date=date2, quantity=1, price=1, buy=False))  # earned 1
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.b, date=date3, quantity=3, price=3))  # spent 9
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.b, date=date4, quantity=2, price=1))  # spent 2
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.b, date=date2, quantity=1, price=1, buy=False))  # earned 1
        self.transactions.append(UserStockTransactions.objects.create(
            user=self.user, company=self.b, date=date5, quantity=4, price=3))  # spent 12

    def test_active(self):
        actives = Company.objects.active()
        self.assertTrue(self.a in actives and self.b in actives)

    def test_weekly(self):
        weekly_prices = Company.objects.weekly(datetime=date(year=2022, month=7, day=7)).filter(
            name='A').values_list('price__closing', flat=True)
        self.assertTrue(set(weekly_prices) == set([1, 2, 3, 4]))

    def test_followed(self):
        followed1 = UserFollowedCompanies.objects.user_followed_companies(
            self.user)
        followed2 = UserFollowedCompanies.objects.user_followed_companies(
            self.user.pk)
        self.assertQuerysetEqual(followed1, followed2, ordered=False)
        companies = [
            followed_company.company for followed_company in followed1]
        self.assertTrue(self.a in companies and self.b in companies)

    def test_stocks_of_user(self):
        stocks1 = UserStockTransactions.objects.stocks_of_user(self.user)
        stocks2 = UserStockTransactions.objects.stocks_of_user(self.user.pk)
        self.assertQuerysetEqual(stocks1, stocks2, ordered=False)
        self.assertEqual(set(stocks1), set(self.transactions))

    def test_bought_stocks_of_user(self):
        stocks1 = UserStockTransactions.objects.bought_stocks_of_user(
            self.user)
        stocks2 = UserStockTransactions.objects.bought_stocks_of_user(
            self.user.pk)
        transactions = [
            transaction for transaction in self.transactions if transaction.buy]
        self.assertQuerysetEqual(stocks1, stocks2, ordered=False)
        self.assertEqual(set(stocks1), set(transactions))

    def test_money_on_buys(self):
        money = UserStockTransactions.objects.money_spent_on_buys(self.user)
        self.assertEqual(money, 41.0)

    def test_money_on_sells(self):
        money = UserStockTransactions.objects.money_earned_on_sells(self.user)
        self.assertEqual(money, 19.0)

    def test_average_price(self):
        money = UserStockTransactions.objects.bought_stocks_of_user(
            self.user).values('company').annotate_average_price()
        money = list(money)
        first_company = {'company': 1, 'qty': 8, 'weighted_avg': 2.125}
        second_company = {'company': 2, 'qty': 10, 'weighted_avg': 2.4}
        self.assertTrue(first_company in money and second_company in money)

    def test_summarized(self):
        summary = summarize_price(self.transactions)
        self.assertTrue(summary['A']['price'] == (((2*1+5*2)/7)*4 + 5)/5)
        self.assertTrue(summary['A']['quantity'] == 3)
        self.assertTrue(summary['B']['price'] == (((3*3+2*1)/5)*4 + 12)/8)
        self.assertTrue(summary['B']['quantity'] == 8)
