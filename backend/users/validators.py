import re

from django.core.exceptions import ValidationError


def validation_username(value):
    """Проверяет валидность никнейма."""

    if not bool(re.match(r'^[\w.@+-]+\Z', value)):
        raise ValidationError(
            'Недопустимые символы в никнейме'
        )
    if value.lower() == 'me':
        raise ValidationError(
            'Никнейм не может быть "me"'
        )
    return value
