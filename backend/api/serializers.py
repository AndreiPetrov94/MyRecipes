from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.utils import (
    Base64ImageField,
)
# from recipes.models import (
#     Tag,
#     Recipe,
#     Ingredient,
#     RecipeIngredient,
#     Favorite,
#     ShoppingList
# )
from users.models import (
    User,
    # Subscription
)
# from users.validators import (
#     validation_password,
#     validation_username
# ) 


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор получения пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.follower.filter(user=request.user).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
