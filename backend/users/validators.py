import re

from django.core.exceptions import ValidationError


def validation_password_length(value):
    """Проверяет валидность минимальной длины пароля."""

    if len(value) < 8:
        raise ValidationError(
            'Пароль должен содержать минимум 8 символов.'
        )


def validation_username(value):
    """Проверяет валидность никнейма."""

    if not bool(re.match(r'^[\w.@+-]+\Z', value)):
        raise ValidationError(
            'Никнейм содержит недопустимые символы.'
        )
    if value.lower() == 'me':
        raise ValidationError(
            'Никнейм не может быть "me"'
        )
    return value
