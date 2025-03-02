from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.constants import (MAX_LENGTH_INGREDIENT_NAME,
                                MAX_LENGTH_MEASUREMENT_UNIT,
                                MAX_LENGTH_RECIPE_NAME, MAX_LENGTH_TAG_NAME,
                                MAX_LENGTH_TAG_SLUG, MAX_VALUE_COOKING_TIME,
                                MIN_VALUE_COOKING_TIME,
                                MIN_VALUE_INGREDIENT_AMOUNT)
from recipes.validators import validation_slug
from users.models import User


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True,
        verbose_name='Название тега',
        help_text='Название тега'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
        validators=(validation_slug,),
        verbose_name='Слаг тега',
        help_text='Слаг тега'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        verbose_name='Название ингредиента',
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name='Единица измерения ингредиента',
        help_text='Единица измерения ингредиента'
    )

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_name_measurement_unit'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name='Название рецепта',
        help_text='Название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта'
    )
    image = models.ImageField(
        upload_to='media/recipes/',
        blank=False,
        null=False,
        verbose_name='Изображение',
        help_text='Изображение'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_VALUE_COOKING_TIME,
                'Время приготовления не может быть меньше 1 минуты'
            ),
            MaxValueValidator(
                MAX_VALUE_COOKING_TIME,
                'Время приготовления не может быть меньше 10 080 минут'
            ),
        ),
        verbose_name='Время приготовления в минутах',
        help_text='Время приготовления в минутах'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег рецепта',
        help_text='Тег рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта',
        help_text='Ингредиенты рецепта'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингередиетов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
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
        ordering = ('-id',)
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


class BaseUserRecipeModel(models.Model):
    """Бзаовая модель для Favorite и ShoppingCart."""

    _added_to: str = ''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в {self._added_to}: {self.recipe.name}'


class Favorite(BaseUserRecipeModel):
    """Модель добавления рецептов в избранное."""

    _added_to: str = 'избранное'

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(BaseUserRecipeModel):
    """Модель списка покупок."""

    _added_to: str = 'список покупок'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
