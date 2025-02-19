from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_EMAILFIELD,
    MAX_LENGTH_CHARFIELD_NAME,
    MAX_LENGTH_CHARFIELD_PASSWORD
)
from users.validators import (
    validation_password_length,
    validation_username
)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAILFIELD,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_CHARFIELD_NAME,
        blank=False,
        null=False,
        unique=True,
        validators=(validation_username,),
        verbose_name='Никнейм'
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
        validators=(validation_password_length,),
        verbose_name='Пароль'
    )
    avatar = models.ImageField(
        upload_to='media/avatars/',
        blank=True,
        null=True,
        verbose_name='Автор'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name')

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['author']
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follower'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='taboo_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
