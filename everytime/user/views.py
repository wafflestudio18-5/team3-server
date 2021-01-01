from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import redirect

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer
from user.tokens import TokenGenerator


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        if self.action in ('create', 'login', 'activate'):
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

    @action(detail=False, methods=['POST'])
    def verify(self, request):
        user = request.user
        current_site = get_current_site(request)
        token = TokenGenerator().make_token(user)
        user_id_b64 = urlsafe_base64_encode(force_bytes(user.id))

        subject = '[와브리타임] 학교 인증 확인'
        context = {
            'current_site': current_site,
            'user_id_b64': user_id_b64,
            'token': token
        }
        message = render_to_string('mail.html', context)
        from_email = settings.EMAIL_HOST_USER
        to_email = ['abyss7500@snu.ac.kr']
        send_mail(subject, message, from_email, to_email)
        msg = "Send Mail!"
        return Response({'MSG': msg})

    @action(detail=False, methods=['GET'])
    def activate(self, request):
        user_id_b64 = request.query_params.get('user_id_b64')
        user_id = force_text(urlsafe_base64_decode(user_id_b64))
        token = request.query_params.get('token')
        user = User.objects.get(id=user_id)

        if user is not None and TokenGenerator().check_token(user, token):
            profile = user.profile
            profile.is_verified = True
            profile.save()
            login(request, user)
            return redirect('https://www.waverytime.shop/')
        errmsg = "User is None or Token is Wrong!"
        return Response({'ERR': errmsg}, status=status.HTTP_400_BAD_REQUEST)
