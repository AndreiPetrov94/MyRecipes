from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse

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
    empty_value_display = '-пусто-'


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
    empty_value_display = '-пусто-'

    def save_model(self, request, obj, form, change):
        """Реализация ограничения подписки на себя."""
        if obj.user == obj.author:
            self.message_user(
                request,
                'Нельзя оформить подписку на себя.',
                level=messages.ERROR
            )
            return
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj):
        """Перенаправление на форму создания подписки."""
        if obj.user == obj.author:
            url = reverse('admin:users_subscription_add')
            return HttpResponseRedirect(url)
        return super().response_add(request, obj)

    def response_change(self, request, obj):
        """Перенаправление на форму изменения подписки."""
        if obj.user == obj.author:
            url = reverse(
                'admin:users_subscription_change',
                args=[obj.id]
            )
            return HttpResponseRedirect(url)
        return super().response_change(request, obj)
