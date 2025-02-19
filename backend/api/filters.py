from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Tags'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_list = filters.BooleanFilter(
        method='filter_is_in_shopping_list'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_list'
        )

    def get_is_favorited(self, queryset, filter_name, filter_value):
        if filter_value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_list(self, queryset, filter_name, filter_value):
        if filter_value:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
