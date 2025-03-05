from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from foodgram.constants import INLINE_EXTRA_VALUE


class RecipeIngredientsInLine(admin.TabularInline):
    """Управление ингредиентами рецепта."""

    model = RecipeIngredient
    extra = INLINE_EXTRA_VALUE

    def get_formset(self, request, obj=None, **kwargs):
        """Формсет для проверки ингредиентов рецепта."""
        formset = super().get_formset(request, obj, **kwargs)

        def clean(formset_self):
            """Проверка наличия и уникальности ингредиента в рецепте."""
            ingredients = []
            validation_ingredients = False

            for form in formset_self.forms:
                ingredient = form.cleaned_data.get('ingredient')
                deletion_ingredients = form.cleaned_data.get('DELETE', False)

                if ingredient and not deletion_ingredients:
                    validation_ingredients = True

                    if ingredient in ingredients:
                        raise forms.ValidationError(
                            f'Ингредиент "{ingredient}" уже добавлен в рецепт.'
                        )
                    ingredients.append(ingredient)

            if not validation_ingredients:
                raise forms.ValidationError(
                    'Рецепт должен содержать хотя бы один ингредиент.'
                )
        formset.clean = clean
        return formset


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
    empty_value_display = '-пусто-'

    def save_model(self, request, obj, form, change):
        """Реализация ограничения создания ингредиента."""
        if obj.name == obj.measurement_unit:
            self.message_user(
                request,
                'Название и единица измерения ингредиента должны быть разные.',
                level=messages.ERROR
            )
            return
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj):
        """Перенаправление на форму создания ингредиента."""
        if obj.name == obj.measurement_unit:
            url = reverse('admin:recipes_ingredient_add')
            return HttpResponseRedirect(url)
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        """Перенаправление на форму изменения ингредиента."""
        if obj.name == obj.measurement_unit:
            url = reverse(
                'admin:recipes_ingredient_change',
                args=[obj.id]
            )
            return HttpResponseRedirect(url)
        return super().response_change(request, obj)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Управление тегами."""

    list_display = (
        'id',
        'name',
        'slug'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Управление рецептами."""

    inlines = (
        RecipeIngredientsInLine,
        FavoriteInline,
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
        'tags',
        'cooking_time'
    )
    search_fields = (
        'name',
        'author__username'
    )
    list_filter = ('tags',)

    @admin.display(description='Добавлено в избранное')
    def in_favorite(self, obj):
        """Отображение кол-ва пользователей, добавивших рецепт в избранное."""
        return f'{obj.favorites.count()} пользоват.'


class AuthorRecipeAdminMixin:
    """Миксин ограничения повторяющихся рецептов."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'recipe__name'
    )
    list_filter = ('user',)
    empty_value_display = '-пусто-'

    def check_recipe(self, obj):
        """Проверка рецепта."""
        return self.model.objects.filter(
            user=obj.user,
            recipe=obj.recipe
        ).exists()

    def save_model(self, request, obj, form, change):
        """Проверка наличия рецепта в списке."""
        if self.check_recipe(obj):
            self.message_user(
                request,
                f'Этот рецепт уже добавлен в {self._added_to}.',
                level=messages.ERROR
            )
            return
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj):
        """Обработка ошибки при добавлении повторяющегося рецепта."""
        if self.check_recipe(obj):
            url = reverse(f'admin:recipes_{self.model.__name__.lower()}_add')
            return HttpResponseRedirect(url)
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        """Обработка ошибки при изменении повторяющегося рецепта."""
        if self.check_recipe(obj):
            url = reverse(
                f'admin:recipes_{self.model.__name__.lower()}_change',
                args=[obj.id]
            )
            return HttpResponseRedirect(url)
        return super().response_change(request, obj)


@admin.register(Favorite)
class FavoriteAdmin(AuthorRecipeAdminMixin, admin.ModelAdmin):
    """Управление избранными рецептами."""

    _added_to = 'избранное'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(AuthorRecipeAdminMixin, admin.ModelAdmin):
    """Управление списком покупок."""

    _added_to = 'список покупок'
