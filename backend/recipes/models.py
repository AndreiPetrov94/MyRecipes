from django.db import models

from backend.foodgram.constants import (
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT
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
