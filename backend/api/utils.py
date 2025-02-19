import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField, ValidationError

from recipes.models import Ingredient


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
