from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.utils import Base64ImageField, check_user_status
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription, User
from users.validators import validation_password_length, validation_username


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    password = serializers.CharField(
        validators=(validation_password_length,),
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

    def validation_username(self, value):
        """Проверяет валидность никнейма."""
        return validation_username(value)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для получения данных о пользователе."""

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
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField(allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления подписки."""

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора.'
            )
        ]

    def validate_author(self, value):
        """Проверяет валидность подписки на себя."""
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя оформить подписку на себя.'
            )
        return value

    def to_representation(self, instance):
        """Возвращает детальную информацию о подписке."""
        return SubscriptionDetailSerializer(
            instance.author,
            context=self.context
        ).data


class SubscriptionDetailSerializer(CustomUserSerializer):
    """Сериализатор списка подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Возвращает список рецептов автора."""
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        return RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        """Возвращает общее количество рецептов автора."""
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор представления ингредиентов в рецепте."""

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
    """Сериализатор для получения информации о рецептах."""

    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном."""
        return check_user_status(
            self.context.get('request'),
            obj,
            Favorite
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в списке покупок."""
        return check_user_status(
            self.context.get('request'),
            obj,
            ShoppingCart
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientPostSerializer(
        many=True,
        source='recipe_ingredients',
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        """Валидация входных данных для создания/обновления рецепта."""
        if not data.get('recipe_ingredients'):
            raise serializers.ValidationError(
                {'ingredients': 'Это поле обязательно!'}
            )
        if not data.get('tags'):
            raise serializers.ValidationError(
                {'tags': 'Это поле обязательно!'}
            )
        if self.context['request'].method == 'POST':
            name = data.get('name')
            if Recipe.objects.filter(name=name).exists():
                raise serializers.ValidationError(
                    {'name': 'Такой рецепт уже существует!'}
                )
        return data

    def validate_tags(self, value):
        """Проверяет валидность тегов."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Тег должен быть уникальным!'
            )
        return value

    def validate_ingredients(self, value):
        """Проверяет валидность ингредиентов."""
        ingredient_ids = [ingredient['id'] for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Нельзя добавлять один и тот же ингредиент несколько раз!'
            )
        return value

    def create_ingredients(self, ingredients, recipe):
        """Создает связи между рецептом и ингредиентами."""
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients_data, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Преобразует данные рецепта в формат вывода."""
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


class AbstractAuthorRecipeSerializer(serializers.ModelSerializer):
    """Абстрактный сериализатор для избранного и списка покупок."""

    _added_to: str = ''

    class Meta:
        abstract = True
        fields = (
            'author',
            'recipe'
        )
        read_only_fields = ('author',)

    def validate(self, attrs):
        """Проверяет, не добавлен ли рецепт уже в указанное место."""
        if self.Meta.model.objects.filter(**attrs).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {self._added_to}.'
            )
        return attrs

    def to_representation(self, instance):
        """Преобразует рецепт в удобный для вывода формат."""
        if isinstance(instance, Recipe):
            return RecipeShortSerializer(
                instance,
                context=self.context
            ).data
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context
        ).data


class FavoriteRecipeSerializer(AbstractAuthorRecipeSerializer):
    """Сериализатор избранных рецептов."""

    _added_to = 'избранное'

    class Meta(AbstractAuthorRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(AbstractAuthorRecipeSerializer):
    """Сериализатор списка покупок."""

    _added_to = 'список покупок'

    class Meta(AbstractAuthorRecipeSerializer.Meta):
        model = ShoppingCart
