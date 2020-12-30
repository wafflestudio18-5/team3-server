from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    university = serializers.CharField(source='profile.university')
    year = serializers.IntegerField(source='profile.year')
    phone = serializers.CharField(source='profile.phone')
    is_verified = serializers.BooleanField(source='profile.is_verified')

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'nickname',
            'university',
            'year',
            'phone',
            'email',
            'is_verified',
            'last_login',
            'date_joined',
        )

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile = validated_data.pop('profile')
        nickname = profile.pop('nickname')
        university = profile.pop('university')
        year = profile.pop('year')
        phone = profile.pop('phone')

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        UserProfile.objects.create(user=user, nickname=nickname, university=university, year=year, phone=phone)
        return user
