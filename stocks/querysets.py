from __future__ import annotations

from django.db import models
from django.utils import timezone
from datetime import timedelta
import django.contrib.auth as auth
from django.db.models.aggregates import Sum
from django.db.models import F


class CompanyQuerySet(models.QuerySet):

    def active(self):
        return self.filter(active=True)

    def weekly(self, datetime=timezone.now()):
        return self.active().filter(price__date__gte=datetime-timedelta(days=7)).order_by('-price__date')

    def weekly_change(self):
        week = self.weekly()
        return week.first() - week.last()

    def weekly_change_percentage(self):
        week = self.weekly()
        return 100*(week.first()/week.last() - 1)


class PriceQuerySet(models.QuerySet):
    def last_week(self):
        return self.order_by('-date')[:5]

    def recent_days_first(self, abbreviation):
        return self.filter(company__abbreviation=abbreviation).order_by('-date')

    def recent_n_days(self, abbreviation, n):
        return self.recent_days_first(abbreviation)[:n]

    def far_days_first(self, abbreviation):
        return self.filter(company__abbreviation=abbreviation).order_by('date')

    def far_days_first_by_companies(self, abbreviation):
        return self.filter(company__abbreviation__in=abbreviation).order_by('date')

    def recent_days_first_by_companies(self, abbreviation):
        return self.filter(company__abbreviation__in=abbreviation).order_by('-date')


class UserFollowedCompaniesQuerySet(models.QuerySet):
    def user_followed_companies(self, user) -> UserFollowedCompaniesQuerySet:
        if isinstance(user, auth.models.User):
            user = user.pk
        return self.filter(user__pk=user)

    def user_followed_company_by_abbreviation(self, user, company) -> UserFollowedCompaniesQuerySet:
        if isinstance(user, auth.models.User):
            user = user.pk
        return self.filter(user__pk=user, company__abbreviation=company)


class UserStockTransactionsQuerySet(models.QuerySet):
    def stocks_of_user(self, user):
        if isinstance(user, auth.models.User):
            user = user.pk
        return self.filter(user__pk=user)

    def bought_stocks_of_user(self, user):
        if isinstance(user, auth.models.User):
            user = user.pk
        return self.filter(user__pk=user, buy=True)

    def annotate_average_price(self):
        return self.annotate(qty=Sum('quantity'), weighted_avg=Sum(F('quantity') * F('price')) / Sum('quantity'))

    def money_spent_on_buys(self, user):
        if isinstance(user, auth.models.User):
            user = user.pk
        return self.filter(user__pk=user, buy=True).aggregate(spent=Sum(F('quantity')*F('price')))['spent']

    def money_earned_on_sells(self, user):
        if isinstance(user, auth.models.User):
            user = user.pk
        return self.filter(user__pk=user, buy=False).aggregate(earned=Sum(F('quantity')*F('price')))['earned']
