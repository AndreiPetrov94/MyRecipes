from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

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

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserGetSerializer(UserSerializer):
    """Сериализатор получения пользователя."""

    avatar = Base64ImageField(allow_null=True, required=False)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.follower.filter(user=request.user).exists()
        return False

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


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
