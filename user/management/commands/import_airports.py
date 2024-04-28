import csv
from django.core.management.base import BaseCommand
from user.models import AirportLOCID

class Command(BaseCommand):
    help = 'Import airports from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The CSV file path')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']
        with open(csv_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row
            for row in reader:
                try:
                    print(locid=row[0])
                    AirportLOCID.objects.create(
                        locid=row[0],
                        location=row[1],
                        # Map other fields accordingly
                    )
                except:
                    pass
            self.stdout.write(self.style.SUCCESS('Successfully imported airports'))
