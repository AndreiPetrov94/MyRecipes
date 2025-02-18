# from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.utils import (
    Base64ImageField,
    check_user_status
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
    User,
    Subscription
)


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
            return obj.following.filter(user=request.user).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(
        allow_null=False,
        required=True
    )

    class Meta:
        model = User
        fields = (
            'avatar',
        )


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscribe
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=("user", "author"),
                message=ERROR_MESSAGES["duplicate_subscription"],
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["author"]:
            raise ValidationError(ERROR_MESSAGES["self_subscribe"])
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return UserSubscribeRepresentSerializer(
            instance.author, context={"request": request}
        ).data


class UserSubscribeRepresentSerializer(UserGetSerializer):
    """Сериализатор получения информации о подписке."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        return RecipeShortSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
















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


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор получения информации о рецептах."""

    author = CustomUserSerializer(
        read_only=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'cooking_time',
            'author',
            'tags',
            'ingredients'
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном."""
        request = self.context.get('request')
        return check_user_status(request, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в списке покупок."""
        request = self.context.get('request')
        return check_user_status(request, obj, ShoppingList)


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientPostSerializer(
        many=True,
        source="recipe_ingredients",
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        """Проверяет валидность тега."""
        if not value:
            raise serializers.ValidationError(
                'БУ! Испугался? Друг необходимо добавить тег.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'БУ! Испугался? Друг теги должны быть уникальны.'
            )
        return value

    def validate_ingredients(self, value):
        """Проверяет валидность ингредиента."""
        if not value:
            raise serializers.ValidationError(
                'БУ! Испугался? Друг необходимо добавить ингредиенты.'
            )
        ingredients_list = []
        for item in value:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    'БУ! Испугался? Друг данного ингредиента нет в базе данных'
                )
            if ingredient in ingredients_list:
                raise ValidationError(
                    'БУ! Испугался? Друг ингредиенты должны быть уникальны.'
                )
            ingredients_list.append(ingredient)
        return value

    def create(self, validated_data):
        """Создание рецепта."""
        request = self.context.get('request')
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)

        recipe_ingredients = []
        existing_ingredients = {
            ri.ingredient.id: ri
            for ri in RecipeIngredient.objects.filter(recipe=instance)
        }
        for item in ingredients:
            ingredient_id = item['id']
            amount = item['amount']

            if ingredient_id in existing_ingredients:
                existing_ingredients[ingredient_id].amount = amount
                existing_ingredients[ingredient_id].save()
            else:
                recipe_ingredients.append(
                    RecipeIngredient(
                        recipe=instance,
                        ingredient_id=ingredient_id,
                        amount=amount,
                    )
                )
        if recipe_ingredients:
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразует рецепт в удобный для вывода формат."""
        return RecipeGetSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'user'
            'name',
            'image',
            'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='БУ! Испугался? Друг рецепт уже находится в избранном.'
            )
        ]

    def to_representation(self, instance):
        """Преобразует рецепт в удобный для вывода формат."""
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe, context={'request': request}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingList
        fields = (
            'id',
            'user'
            'name',
            'image',
            'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='БУ! Испугался? Друг рецепт добавлен в список покупок.'
            )
        ]

    def to_representation(self, instance):
        """Преобразует рецепт в удобный для вывода формат."""
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe, context={'request': request}
        ).data
