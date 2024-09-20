"""Import ingredients from JSON files."""

import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Import ingredients from JSON files."""

    help = 'Import ingredients from JSON files'

    def handle(self, *args, **options):
        """Import ingredients from JSON files."""
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.import_from_json(os.path.join(data_dir, 'ingredients.json'))
        self.stdout.write(self.style.SUCCESS(
            'Successfully imported ingredients'))

    def import_from_json(self, filename):
        """Import ingredients from JSON file."""
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
