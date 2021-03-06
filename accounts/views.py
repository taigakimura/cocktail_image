from django.db import transaction
from django.http import Http404
from django.core.exceptions import PermissionDenied
from .serializer import AccountSerializer
from .models import Account

from rest_framework import status, permissions, generics
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# ユーザ作成のView(POST)
class AuthRegister(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @transaction.atomic
    def post(self, request, format=None):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ユーザ情報取得のView(GET)
class AuthInfoGetView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get(self, request, format=None):
        return Response(data={
            'user_id': request.user.user_id,
            'user_name': request.user.user_name,
            'email': request.user.email,
            },
            status=status.HTTP_200_OK)


# ユーザ情報更新のView(PUT)
class AuthInfoUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AccountSerializer
    lookup_field = 'user_name'
    queryset = Account.objects.all()

    def get_object(self):
        try:
            if self.request.data['before_user_name'] == self.request.user.user_name:
                instance = self.queryset.get(user_name=self.request.user)
                return instance
            else:
                raise PermissionDenied
        except Account.DoesNotExist:
            raise Http404
        except KeyError:
            try:
                if self.request.data['user_name'] == self.request.user.user_name and self.request.user.check_password(self.request.data['before_password']):
                    instance = self.queryset.get(user_name=self.request.user)
                    return instance
                else:
                    raise PermissionDenied
            except KeyError:
                raise PermissionDenied


# ユーザ削除のView(DELETE)
class AuthInfoDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AccountSerializer
    lookup_field = 'user_name'
    queryset = Account.objects.all()

    def get_object(self):
        try:
            instance = self.queryset.get(user_name=self.request.user)
            return instance
        except Account.DoesNotExist:
            raise Http404

