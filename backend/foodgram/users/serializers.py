from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name",
                  "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        request_user = self.context['request'].user
        if isinstance(request_user, AnonymousUser):
            return False

        get_user = obj.id
        is_subscribed = Subscribe.objects.filter(
            user_id=request_user, author_id=get_user).exists()
        return is_subscribed
