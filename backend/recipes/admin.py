from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from foodgram.constants import INLINE_EXTRA_VALUE


class RecipeIngredientsInLine(admin.TabularInline):
    """Управление ингредиентами рецепта."""

    model = RecipeIngredient
    extra = INLINE_EXTRA_VALUE


class ShoppingCartInline(admin.StackedInline):
    """Управление списком покупок."""

    model = ShoppingCart


class FavoriteInline(admin.StackedInline):
    """Управление избранными рецептами."""
    model = Favorite


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Управление ингредиентами."""

    inlines = (
        RecipeIngredientsInLine,
    )
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_display_links = ('name',)
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
    inlines = (
        FavoriteInline,
        RecipeIngredientsInLine,
        ShoppingCartInline
    )

    list_display = (
        'name',
        'author',
        'in_favorite'
    )
    list_display_links = ('name',)
    fields = (
        'name',
        'author',
        'text',
        'tags'
    )
    search_fields = (
        'name',
        'author__username'
    )
    list_filter = ('tags',)

    @admin.display(description='Добавлено в избранное')
    def in_favorite(self, obj):
        return f'{obj.favorites.count()} пользоват.'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Управление списком покупок."""
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Управление избранными рецептами."""
    pass
