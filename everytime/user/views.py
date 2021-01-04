from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.db.models import Count, Model

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.models import UserProfile
from user.serializers import UserSerializer
from user.tokens import TokenGenerator


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        if self.action in ('create', 'login', 'activate', 'university', 'check'):
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

        user = authenticate(request, username=username, password=password)
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

    # POST http://api.waverytime.shop/user/verify/
    @action(detail=False, methods=['POST'])
    def verify(self, request):
        user = request.user
        current_site = 'http://localhost:8000' if settings.LOCAL else 'http://api.waverytime.shop'
        token = TokenGenerator().make_token(user)
        user_id_b64 = urlsafe_base64_encode(force_bytes(user.id))

        subject = '[와브리타임] 학교 인증 확인'
        context = {
            'current_site': current_site,
            'user_id_b64': user_id_b64,
            'token': token
        }
        html_message = render_to_string('mail.html', context)
        from_email = settings.EMAIL_HOST_USER
        to_email = [user.email]
        send_mail(subject, None, from_email, to_email, html_message=html_message)
        msg = "Send Mail!"
        return Response({'MSG': msg})

    # GET http://api.waverytime.shop/user/activate?user_id_b64={user_id_b64}&token={token}
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

    # GET http://api.waverytime.shop/user/university/
    @action(detail=False, methods=['GET'])
    def university(self, request):
        result = UserProfile.objects.values('university').annotate(Count('id'))
        return Response(result)

    # GET http://api.waverytime.shop?username={username}
    # GET http://api.waverytime.shop?nickname={nickname}
    # GET http://api.waverytime.shop?phone={phone}
    # GET http://api.waverytime.shop?email={email}
    @action(detail=False, methods=['GET'])
    def check(self, request):
        username = request.query_params.get('username')
        if username and User.objects.filter(username=username).exists():
            errmsg = "This username already exists!"
            return Response({'ERR': errmsg}, status=status.HTTP_400_BAD_REQUEST)

        nickname = request.query_params.get('nickname')
        if nickname and UserProfile.objects.filter(nickname=nickname).exists():
            errmsg = "This nickname already exists!"
            return Response({'ERR': errmsg}, status=status.HTTP_400_BAD_REQUEST)

        phone = request.query_params.get('phone')
        if phone and UserProfile.objects.filter(phone=phone).exists():
            errmsg = "This phone number already exists!"
            return Response({'ERR': errmsg}, status=status.HTTP_400_BAD_REQUEST)

        email = request.query_params.get('email')
        if email and User.objects.filter(email=email).exists():
            errmsg = "This email already exists!"
            return Response({'ERR': errmsg}, status=status.HTTP_400_BAD_REQUEST)

        msg = "Clear!"
        return Response({'MSG': msg}, status=status.HTTP_200_OK)
