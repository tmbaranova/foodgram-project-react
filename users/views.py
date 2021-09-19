from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.settings import api_settings


from .models import User
from .serializers import (UserSerializer)

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = 'username'
#
#     permission_classes = [AllowAny]
#     filter_backends = [filters.SearchFilter]
#     pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
#     search_fields = ('user__username',)
#
#     @action(
#         methods=['get'],
#         permission_classes=[IsAuthenticated],
#         detail=False,
#         url_path='me',
#         url_name='me'
#     )
#     def me(self, request, *args, **kwargs):
#         user = self.request.user
#         serializer = self.get_serializer(user)
#         return Response(serializer.data)