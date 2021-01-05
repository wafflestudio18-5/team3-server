import re
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
            'last_name',
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
        email = data.get('email')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError("This email is invalid!")

        profile = data.get('profile')
        if profile:
            phone = profile.get('phone')
            if phone:
                reg = re.compile(r'\d{3}-\d{4}-\d{4}')
                if not reg.match(phone):
                    raise serializers.ValidationError("This phone is invalid!")

        return data

    @transaction.atomic
    def create(self, validated_data):
        # username - unique
        username = validated_data.get('username')
        if not username:
            raise serializers.ValidationError("Username must be set!")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username already exists!")

        # email - unique
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError("Email must be set!")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email already exists!")

        # last_name
        last_name = validated_data.get('last_name')
        if not last_name:
            raise serializers.ValidationError("Name must be set!")

        profile = validated_data.pop('profile')

        # nickname - unique
        nickname = profile.pop('nickname')
        if not nickname:
            raise serializers.ValidationError("Nickname must be set!")
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("This nickname already exists!")

        # university
        university = profile.pop('university')
        if not university:
            raise serializers.ValidationError("University must be set!")

        # year
        year = profile.pop('year')
        if not year:
            raise serializers.ValidationError("Year must be set!")

        # phone - unique
        phone = profile.pop('phone')
        if not phone:
            raise serializers.ValidationError("Phone number must be set!")
        if UserProfile.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("This phone already exists!")

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        UserProfile.objects.create(user=user, nickname=nickname, university=university, year=year, phone=phone)
        return user

    @transaction.atomic
    def update(self, user, validated_data):
        # email
        email = validated_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email already exists!")

        # nickname
        profile = validated_data.pop('profile', None)
        if profile:
            nickname = profile.get('nickname')
            if nickname and UserProfile.objects.filter(nickname=nickname).exists():
                raise serializers.ValidationError("This nickname already exists!")
            profile = user.profile
            profile.nickname = nickname
            profile.save()

        return super(UserSerializer, self).update(user, validated_data)

