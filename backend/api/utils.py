import base64

from django.http import HttpResponse
from django.db.models import Sum
from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField, ValidationError
from rest_framework.response import Response
from rest_framework import status

from recipes.models import Ingredient, RecipeIngredient


class Base64ImageField(ImageField):
    """Поле для декодировки изображений в формате Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                img_format, img_str = data.split(';base64,')
                ext = img_format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(img_str), name=f'image.{ext}'
                )
            except (ValueError, base64.binascii.Error):
                raise ValidationError(
                    'Неверные данные изображения в формате Base64.'
                )
        return super().to_internal_value(data)


def check_user_status(request, obj, model):
    """Проверка рецепта."""
    return (
        request
        and request.user.is_authenticated
        and model.objects.filter(user=request.user, recipe=obj).exists()
    )


def validate_unique_ingredients(value):
    """Проверяет наличие и уникальность игредиента."""
    if not value:
        raise ValidationError(
            'БУ! Испугался? Друг необходимо добавить ингредиенты.'
        )
    ingredients_list = []
    for item in value:
        try:
            ingredient = Ingredient.objects.get(id=item['id'])
        except Ingredient.DoesNotExist:
            raise ValidationError(
                'БУ! Испугался? Друг данного ингредиента нет в базе данных'
            )
        if ingredient in ingredients_list:
            raise ValidationError(
                'БУ! Испугался? Друг ингредиенты должны быть уникальны.'
            )
        ingredients_list.append(ingredient)
    return value


def validate_unique_items(value, item_name):
    """Проверяет наличие и уникальность значения."""
    if not value:
        raise ValidationError(
            f'БУ! Испугался? Друг необходимо добавить {item_name}.'
        )
    if len(value) != len(set(value)):
        raise ValidationError(
            f'БУ! Испугался? Друг {item_name} должны быть уникальны.'
        )
    return value


def get_shopping_cart(request):
    """Получить файл со списком покупок."""
    user = request.user
    if not user.shopping_carts.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ingredients = (
        RecipeIngredient.objects.filter(recipe__shopping_carts__user=request.user)
        .values(
            "ingredient__name",
            "ingredient__measurement_unit",
        )
        .annotate(ingredient_amount=Sum("amount"))
    )
    shopping_cart = f"Список покупок пользователя {user}:\n"

    for ingredient in ingredients:
        name = ingredient["ingredient__name"]
        unit = ingredient["ingredient__measurement_unit"]
        amount = ingredient["ingredient_amount"]
        shopping_cart += f"\n{name} - {amount}/{unit}"

    file_name = f"{user}_shopping_cart.txt"
    response = HttpResponse(shopping_cart, content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename={file_name}"
    return response
