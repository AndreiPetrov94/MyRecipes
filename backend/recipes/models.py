from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from backend.foodgram.constants import (
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    MAX_LENGTH_RECIPE_NAME,
    MIN_VALUE_COOKING_TIME
)
from backend.recipes.validators import validation_slug
from backend.users.models import User


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
        blank=False,
        null=False,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Тег рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        null=False,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )
