import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField, ValidationError


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
