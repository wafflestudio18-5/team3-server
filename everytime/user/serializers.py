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
            'last_name',
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
        print("Validating...")
        username = data.get('username')
        if not username:
            raise serializers.ValidationError("Username must be set!")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This username already exists!")

        email = data.get('email')
        if not email:
            raise serializers.ValidationError("Email must be set!")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email already exists!")

        last_name = data.get('last_name')
        if not last_name:
            raise serializers.ValidationError("Last Name must be set!")
        if User.objects.filter(last_name=last_name).exists():
            raise serializers.ValidationError("This last name already exists!")

        profile = data.get('profile')
        nickname = profile.get('nickname')
        if not nickname:
            raise serializers.ValidationError("Nickname must be set!")
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError("This nickname already exists!")

        phone = profile.get('phone')
        if not phone:
            raise serializers.ValidationError("Phone number must be set!")
        if UserProfile.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("This phone already exists!")
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
