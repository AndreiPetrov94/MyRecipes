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
    ShoppingList
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
        if request and request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True, allow_null=False)

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
        # if not value:
        #     raise serializers.ValidationError(
        #         'БУ! Испугался? Друг необходимо добавить тег.'
        #     )
        # if len(value) != len(set(value)):
        #     raise serializers.ValidationError(
        #         'БУ! Испугался? Друг теги должны быть уникальны.'
        #     )
        return validate_unique_items(value, 'теги')

    def validate_ingredients(self, value):
        """Проверяет валидность ингредиента."""
        # if not value:
        #     raise serializers.ValidationError(
        #         'БУ! Испугался? Друг необходимо добавить ингредиенты.'
        #     )
        # ingredients_list = []
        # for item in value:
        #     try:
        #         ingredient = Ingredient.objects.get(id=item['id'])
        #     except Ingredient.DoesNotExist:
        #         raise ValidationError(
        #             'БУ! Испугался? Друг данного ингредиента нет в базе данных'
        #         )
        #     if ingredient in ingredients_list:
        #         raise ValidationError(
        #             'БУ! Испугался? Друг ингредиенты должны быть уникальны.'
        #         )
        #     ingredients_list.append(ingredient)
        # return value
        return validate_unique_ingredients(value)

    def create(self, validated_data):
        """Создание рецепта."""
        # request = self.context.get('request')
        # ingredients_data = validated_data.pop('recipe_ingredients')
        # tags = validated_data.pop('tags')
        # recipe = Recipe.objects.create(author=request.user, **validated_data)
        # recipe.tags.set(tags)
        # recipe_ingredients = [
        #     RecipeIngredient(
        #         recipe=recipe,
        #         ingredient_id=item['id'],
        #         amount=item['amount']
        #     )
        #     for item in ingredients_data
        # ]
        # RecipeIngredient.objects.bulk_create(recipe_ingredients)
        # return recipe

        ingredients = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe, ingredient_id=item['id'], amount=item['amount'])
                for item in ingredients
            ]
        )
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        # ingredients = validated_data.pop('recipe_ingredients')
        # tags = validated_data.pop('tags')
        # instance.tags.clear()
        # instance.tags.set(tags)
        # RecipeIngredient.objects.filter(recipe=instance).delete()
        # super().update(instance, validated_data)

        # recipe_ingredients = []
        # existing_ingredients = {
        #     ri.ingredient.id: ri
        #     for ri in RecipeIngredient.objects.filter(recipe=instance)
        # }
        # for item in ingredients:
        #     ingredient_id = item['id']
        #     amount = item['amount']

        #     if ingredient_id in existing_ingredients:
        #         existing_ingredients[ingredient_id].amount = amount
        #         existing_ingredients[ingredient_id].save()
        #     else:
        #         recipe_ingredients.append(
        #             RecipeIngredient(
        #                 recipe=instance,
        #                 ingredient_id=ingredient_id,
        #                 amount=amount,
        #             )
        #         )
        # if recipe_ingredients:
        #     RecipeIngredient.objects.bulk_create(recipe_ingredients)
        # instance.save()
        # return instance

        ingredients = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=instance,
                    ingredient_id=item['id'],
                    amount=item['amount']
                )
                for item in ingredients
            ]
        )
        super().update(instance, validated_data)
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


class ShoppingListSerializer(AbstractAuthorRecipeSerializer):
    """Сериализатор списка покупок."""

    _added_to = 'список покупок'

    class Meta(AbstractAuthorRecipeSerializer.Meta):
        model = ShoppingList



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


# class ShoppingListSerializer(serializers.ModelSerializer):
#     """Сериализатор списка покупок."""

#     class Meta:
#         model = ShoppingList
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