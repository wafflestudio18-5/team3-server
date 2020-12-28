from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    is_certified = models.BooleanField(default=False)
    nickname = models.CharField(max_length=150, blank=False, unique=True)
    university = models.CharField(max_length=150, blank=False)
    year = models.PositiveSmallIntegerField()
    phone = models.CharField(max_length=150, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
