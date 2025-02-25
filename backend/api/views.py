from django.shortcuts import redirect
from djoser.views import UserViewSet
from django.views.decorators.http import require_GET
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    CustomUserSerializer,
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    SubscriptionDetailSerializer,
    SubscriptionSerializer,
    TagSerializer
)
from api.utils import check_recipe_action, get_shopping_cart
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import User, Subscription


class CustomUserViewSet(UserViewSet):
    """Вьюсет для управления пользователями и подписками."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        """Получение данных текущего пользователя."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['PUT'],
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        """Обновление аватара пользователя."""
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        """Удаление аватара пользователя."""
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        url_name='subscriptions'
    )
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionDetailSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Добавление/удаление подписки на автора."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'POST':
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset = Subscription.objects.create(author=author, user=user)
            serializer = SubscriptionSerializer(
                queryset,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                    user=user,
                    author=author
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.filter(
                user=user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action in ('get-link', 'list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        """Создание нового рецепта."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Аутентификация требуется.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(AllowAny,),
        url_path='get-link',
        url_name='get-link'
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        rev_link = reverse(
            'get_short_link',
            args=[recipe.pk]
        )
        return Response(
            {'short-link': request.build_absolute_uri(rev_link)},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта из избранного."""
        recipe = self.get_object()
        return check_recipe_action(
            request,
            Favorite,
            recipe,
            FavoriteRecipeSerializer
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из списка покупок."""
        recipe = self.get_object()
        return check_recipe_action(
            request,
            ShoppingCart,
            recipe,
            ShoppingCartSerializer
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        return get_shopping_cart(request)


@require_GET
def get_short_link(request, pk):
    """Переадресация на страницу рецепта."""
    try:
        Recipe.objects.get(pk=pk)
        return redirect(f'/recipes/{pk}/')
    except Exception:
        raise ValidationError(f'Рецепт с ID "{pk}" не найден.')
