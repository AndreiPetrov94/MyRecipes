from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Управление пользователями."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username',
        'first_name'
    )
    list_display_links = ('username',)
    search_fields = ('email', 'username')
    empty_value_display = '-empty-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Управление подписками."""

    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = (
        'user',
        'author'
    )
    empty_value_display = '-empty-'
