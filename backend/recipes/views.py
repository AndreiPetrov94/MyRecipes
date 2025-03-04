from django.shortcuts import reverse
from django.views.decorators.http import require_GET
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe


@require_GET
def get_short_link(request, pk):
    """Переадресация на страницу рецепта."""
    try:
        Recipe.objects.get(pk=pk)
        return reverse('recipes', args=[pk])
    except Exception:
        raise ValidationError(f'Рецепт с ID "{pk}" не найден.')
