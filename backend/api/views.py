from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from django.shortcuts import redirect
from djoser.views import UserViewSet
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

# from api.filters import IngredientFilter, RecipeFilter
# from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    AvatarSerializer,
    SubscribeSerializer,
    SubscriberDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeIngredientSerializer,
    RecipeGetSerializer,
    IngredientPostSerializer,
    RecipeCreateUpdateSerializer,
    RecipeShortSerializer,
    FavoriteRecipeSerializer,
    ShoppingListSerializer
)

from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingList
)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями и подписками."""

    @action(
        detail=False, methods=['GET'], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)




    @action(detail=False, methods=['put', 'delete'], permission_classes=[
        IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        """Управление аватаром пользователя."""
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
                return Response(
                    {'avatar': None},
                    status=status.HTTP_204_NO_CONTENT)
            raise ValidationError({'error': 'Аватар отсутствует'})

        if "avatar" not in request.data:
            return Response(
                {"error": "Поле 'avatar' обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AvatarSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
