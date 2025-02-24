from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.utils import (
    Base64ImageField,
    check_user_status,
    validate_unique_ingredients,
    validate_unique_items
)
from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)
from users.models import User, Subscription
from users.validators import validation_password_length


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
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор добавления|удаления подписки."""

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
                message='БУ! Испугался? Друг ты уже подписан на этого автора.'
            )
        ]

    def validate_author(self, value):
        """Проверяет валидность подписки на себя."""
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'БУ! Испугался? Друг нельзя оформить подписку на себя'
            )
        return value

    def to_representation(self, instance):
        """Преобразует объект подписки в удобный для вывода формат."""
        request = self.context.get('request')
        return SubscriptionDetailSerializer(
            instance.author, context={'request': request}
        ).data


class SubscriptionDetailSerializer(CustomUserSerializer):
    """Сериализатор списка подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
            'avatar'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, obj):
        """Возвращает список рецептов."""
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
        """Возвращает общее количество рецептов."""
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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart')
        read_only_fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном."""
        request = self.context.get('request')
        return check_user_status(request, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в списке покупок."""
        request = self.context.get('request')
        return check_user_status(request, obj, ShoppingCart)


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # id = serializers.IntegerField()

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

    def validate(self, data):
        # Проверяем, что поле 'ingredients' присутствует в запросе
        if 'recipe_ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле обязательно.'}
            )

        # Проверяем, что поле 'tags' присутствует в запросе
        if 'tags' not in data:
            raise serializers.ValidationError(
                {'tags': 'Это поле обязательно.'}
            )

        # Проверяем уникальность названия рецепта при создании
        if self.context['request'].method == 'POST':
            name = data.get('name')
            if Recipe.objects.filter(name=name).exists():
                raise serializers.ValidationError(
                    {'name': 'Такой рецепт уже существует!'}
                )

        return data

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

        # Проверяем уникальность ID ингредиентов
        ingredient_ids = [ingredient['id'] for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Нельзя добавлять один и тот же ингредиент несколько раз.'
            )

        return value

    def create_ingredients(self, ingredients, recipe):
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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
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
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}).data


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
    """Абстрактный сериализатор автора и рецепта."""

    _added_to: str = ''

    class Meta:
        abstract = True
        fields = ('author', 'recipe')
        read_only_fields = ('author',)

    def validate(self, attrs):
        recipe = attrs['recipe']
        user = self.context['request'].user
        if self.Meta.model.objects.filter(author=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'БУ! Испугался? Рецепт добавлен в {self._added_to}.'
            )
        return attrs

    def to_representation(self, instance):
        """Преобразует рецепт в удобный для вывода формат."""
        return RecipeShortSerializer(
            instance.recipe, context=self.context
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



# class FavoriteRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор избранных рецептов."""

#     class Meta:
#         model = Favorite
#         fields = "__all__"
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=model.objects.all(),
#                 fields=('user', 'recipe'),
#                 message='БУ! Испугался? Друг рецепт уже находится в избранном.'
#             )
#         ]

#     def to_representation(self, instance):
#         """Преобразует рецепт в удобный для вывода формат."""
#         request = self.context.get('request')
#         return RecipeShortSerializer(
#             instance.recipe, context={'request': request}
#         ).data


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """Сериализатор списка покупок."""

#     class Meta:
#         model = ShoppingCart
#         fields = "__all__"
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=model.objects.all(),
#                 fields=('user', 'recipe'),
#                 message='БУ! Испугался? Друг рецепт добавлен в список покупок.'
#             )
#         ]

#     def to_representation(self, instance):
#         """Преобразует рецепт в удобный для вывода формат."""
#         request = self.context.get('request')
#         return RecipeShortSerializer(
#             instance.recipe, context={'request': request}
#         ).data