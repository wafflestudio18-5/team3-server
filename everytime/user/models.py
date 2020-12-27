from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    password = models.CharField(max_length=128, null=False, blank=False, unique=True)
    username = models.CharField(max_length=64, null=False, blank=False, unique=True)
    nickname = models.CharField(max_length=64, null=False, blank=False, unique=True)
    university = models.CharField(max_length=64, null=False, blank=False)
    year = models.PositiveSmallIntegerField(null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=64, null=False, blank=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'nickname'
