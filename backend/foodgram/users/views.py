from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny

from .serializers import CustomUserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer(many=True)
    queryset = User.objects.all()
    permission_classes = [AllowAny, ]
