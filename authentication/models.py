from statistics import mode
from django.db import models

from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    choices_currecy = (('PLN', 'PLN'), ('EUR', 'EUR'), ('USD', 'USD'))
    currency = models.CharField(
        choices=choices_currecy, max_length=10, default='PLN')
