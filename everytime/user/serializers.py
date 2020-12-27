from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(allow_blank=False)
    nickname = serializers.CharField(allow_blank=False, write_only=True)
    university = serializers.CharField(allow_blank=False)
    year = serializers.IntegerField(allow_blank=False)
    email = serializers.CharField(allow_blank=False)
    phone = serializers.CharField(allow_blank=False)
    is_active = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'username',
            'nickname',
            'university',
            'year',
            'email',
            'phone',
            'is_active',
            'is_superuser',
            'last_login',
            'date_joined',
        )

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        lst = ['username', 'nickname', 'university', 'year', 'email', 'phone']
        for key in lst:
            val = data.get(key)
            if not val:
                raise serializers.ValidationError(f'{val} must be set')
        return data
