from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from authentication.models import UserProfile


def register_user(login, password):
    user = User.objects.create(
        username=login, password=make_password(password))
    UserProfile.objects.create(user=user)
    return user
