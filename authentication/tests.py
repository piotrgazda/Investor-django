from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

from authentication.registration import register_user


class RegisterTest(TestCase):
    def setUp(self):
        User.objects.create(
            username='user', password=make_password('password'))

    def test_register_existing(self):
        self.assertRaises(IntegrityError, register_user, 'user', 'password')

    def test_register_new(self):
        username, password = 'newuser', 'newpassword'
        user = register_user(username, password)
        authenticated = authenticate(username=username, password=password)
        self.assertIsNotNone(authenticated)
