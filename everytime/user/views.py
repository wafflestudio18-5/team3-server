from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(), )
        return super(UserViewSet, self).get_permissions()

    # POST http://api.waverytime.shop/user/
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except Exception as e:
            print(e)
            errmsg = "Something Wrong!"
            return Response({'ERROR': errmsg}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        data = serializer.data
        data['token'] = user.auth_token.key
        return Response(data, status=status.HTTP_201_CREATED)

    # PUT http://api.waverytime.shop/user/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print("username : ", username)
        print("password : ", password)

        user = authenticate(request, username=username, password=password)
        print(user)
        if user:
            login(request, user)

            data = self.get_serializer(user).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            return Response(data)
        errmsg = "Wrong username or password!"
        return Response({'ERROR': errmsg}, status=status.HTTP_403_FORBIDDEN)

    # POST http://api.waverytime.shop/user/logout/
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        msg = "Logout!"
        return Response({'MSG': msg})
