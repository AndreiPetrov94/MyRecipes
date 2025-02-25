from django.contrib import admin

from foodgram.constants import INLINE_EXTRA_VALUE
from recipes.models import Ingredient, Recipe, Tag


class RecipeIngredientsInLine(admin.TabularInline):
    """Управление ингредиентами рецепта."""

    model = Recipe.ingredients.through
    extra = INLINE_EXTRA_VALUE


class RecipeTagsInLine(admin.TabularInline):
    """Управление тегами рецепта."""

    model = Recipe.tags.through
    extra = INLINE_EXTRA_VALUE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Управление ингредиентами."""

    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Управление тегами."""

    list_display = (
        'id',
        'name',
        'slug'
    )
    search_fields = ('name',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Управление рецептами."""

    list_display = (
        'id',
        'name',
        'text',
        'author'
    )
    search_fields = ('name', 'author')
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)
    list_display_links = ('name',)
    empty_value_display = '-empty-'
