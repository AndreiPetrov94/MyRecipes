from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация с поддержкой параметра 'limit'."""
    page_size_query_param = 'limit'
