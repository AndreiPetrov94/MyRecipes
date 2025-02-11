from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.utils import (
    Base64ImageField,
)
from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingList
)
from users.models import (
    # CustomUser,
    Subscription
)


User = get_user_model()


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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор представления ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )






















class UserRecipeSerializer(CustomUserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, obj):

        request = self.context['request']
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        # Проверяем recipes_limit перед преобразованием в int,
        # чтобы избежать ошибок.
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data
