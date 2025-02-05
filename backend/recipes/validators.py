import re

from django.core.exceptions import ValidationError


def validation_slug(value):
    """Проверяет валидность slug."""

    if not bool(re.match(r'^[-a-zA-Z0-9_]+$', value)):
        raise ValidationError(
            'Слаг содержит недопустимые символы.'
        )
    return value
