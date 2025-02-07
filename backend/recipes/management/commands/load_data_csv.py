import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда загрузки ингредиентов из CVS-файла."""

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.csv'
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                ingredient_name = row[0].strip()
                measurement_unit = row[1].strip()
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    measurement_unit=measurement_unit
                )
