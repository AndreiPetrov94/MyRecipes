from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (
    MAX_LENGTH_EMAILFIELD,
    MAX_LENGTH_CHARFIELD_NAME,
    MAX_LENGTH_CHARFIELD_PASSWORD,
    MAX_LENGTH_CHARFIELD_ROLE,
)
from users.validators import validation_username


class User(AbstractUser):
    """Кастомная модель пользователя."""

    ADMIN = 'admin'
    USER = 'user'
    ROLES = (
        (ADMIN, ADMIN),
        (USER, USER)
    )
    username = models.CharField(
        verbose_name='Никнейм',
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False,
        unique=True,
        validators=(validation_username,)
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=MAX_LENGTH_EMAILFIELD,
        blank=False,
        null=False,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=MAX_LENGTH_CHARFIELD_ROLE,
        choices=ROLES,
        default=USER
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGTH_CHARFIELD_PASSWORD,
        blank=False,
        null=False
    )

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == User.USER

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
