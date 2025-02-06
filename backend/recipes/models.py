from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    MAX_LENGTH_RECIPE_NAME,
    MIN_VALUE_COOKING_TIME,
    MIN_VALUE_INGREDIENT_AMOUNT
)
from recipes.validators import validation_slug
from users.models import User


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True,
        verbose_name="Название тега"
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
        validators=(validation_slug,),
        verbose_name="Слаг"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        unique=True,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name="Единица измерения"
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            )
        ]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        blank=False,
        null=False,
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='media/recipes/',
        blank=False,
        null=False,
        verbose_name='Изображение',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_VALUE_COOKING_TIME,
                'Время приготовления не может быть меньше 1 минуты'
            ),
        ),
        verbose_name='Время приготовления в минутах'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Тег рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингередиетов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_VALUE_INGREDIENT_AMOUNT,
                'Количество ингредиента не может быть меньше 1'
            ),
        ),
        verbose_name='Количество ингредиента'
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class RecipeTags(models.Model):
    """Модель тегов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_list',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe',
        verbose_name='Тег'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        return f'{self.recipe.name} - {self.tag.name}'


class Favorite(models.Model):
    """Модель добавления рецептов в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
