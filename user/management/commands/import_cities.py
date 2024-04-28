# myapp/management/commands/import_cities.py
from django.core.management.base import BaseCommand, CommandError
from user.models import City  
import csv

class Command(BaseCommand):
    help = 'Imports cities from a specified CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import.')

    def handle(self, *args, **options):
        with open(options['csv_file'], mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                City.objects.create(
                    city_name=row['city'],
                    state_id=row['state_id'],
                    state_name=row['state_name'],
                    lat=row['lat'],
                    lng=row['lng']
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported cities'))
