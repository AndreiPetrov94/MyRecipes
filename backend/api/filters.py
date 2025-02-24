from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        label='Название ингредиента'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги рецепта'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты, добавленные в избранное."""
        if not value or not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты, добавленные в список покупок."""
        if not value or not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(shopping_carts__user=self.request.user)
