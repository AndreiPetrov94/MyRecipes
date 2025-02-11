# # from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import generics, viewsets, status
# # from rest_framework.generics import get_object_or_404
# from rest_framework.permissions import (
#     IsAuthenticated,
#     AllowAny
# )
# from rest_framework.response import Response

# # from api.filters import IngredientFilter, RecipeFilter
# # from api.permissions import IsAdminAuthorOrReadOnly
# # from recipes.models import (
# #     Tag,
# #     Recipe,
# #     Ingredient,
# #     RecipeIngredient,
# #     Favorite,
# #     ShoppingList
# # )
# # from users.models import (
# #     User,
# #     Subscription
# # )
# from .serializers import (
#     CustomUserSerializer,
#     AvatarSerializer
# )


# # class UserView(generics.RetrieveAPIView):
# #     """Получение и обновление информации о текущем пользователе."""

# #     serializer_class = CustomUserSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_object(self):
# #         return self.request.user


# class AvatarUpdateView(generics.UpdateAPIView, generics.DestroyAPIView):
#     """Обновление аватара текущего пользователя."""

#     http_method_names = ['put', 'delete']
#     serializer_class = AvatarSerializer
#     permission_classes = [IsAuthenticated]

#     def update(self, request):

#         user = request.user
#         serializer = self.get_serializer(
#             user,
#             data=request.data
#         )

#         if serializer.is_valid():
#             user.avatar.delete()
#             serializer.save()
#             return Response(serializer.data)

#         return Response(
#             serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     def destroy(self, request):

#         user = request.user
#         user.avatar.delete()
#         user.avatar = None
#         user.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)
