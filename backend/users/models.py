from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.foodgram.constants import (
    MAX_LENGTH_EMAILFIELD,
    MAX_LENGTH_CHARFIELD_NAME,
    MAX_LENGTH_CHARFIELD_PASSWORD
)
from users.validators import validation_username


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False,
        unique=True,
        validators=(validation_username,),
        verbose_name='Никнейм'
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAILFIELD,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD_PASSWORD,
        blank=False,
        null=False,
        verbose_name='Пароль'
    )
    avatar = models.ImageField(
        upload_to='media/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name')

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follower'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='taboo_self_follow'
            )
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return self.user
