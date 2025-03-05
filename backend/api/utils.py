import base64

from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ImageField, ValidationError

from recipes.models import RecipeIngredient


class Base64ImageField(ImageField):
    """Поле для декодировки изображений в формате Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                img_format, img_str = data.split(';base64,')
                ext = img_format.split('/')[-1]
                data = ContentFile(
                    base64.b64decode(img_str),
                    name=f'image.{ext}'
                )
            except (ValueError, base64.binascii.Error):
                raise ValidationError(
                    'Неверные данные изображения в формате Base64.'
                )
        return super().to_internal_value(data)


def get_shopping_cart(request):
    """Генерирует файл со списком покупок для текущего пользователя."""
    user = request.user
    if not user.shoppingcarts.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ingredients = (
        RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).select_related('ingredient').values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            ingredient_amount=Sum('amount')
        )
    )
    shopping_cart = f'Список покупок пользователя {user}:\n'

    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_amount']
        shopping_cart += f'\n{name} - {amount}/{unit}'

    file_name = f'{user}_shopping_cart.txt'
    response = HttpResponse(shopping_cart, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
