import csv
from decimal import Decimal

from django.core.management.base import BaseCommand

from route_planner.models import FuelStation


class Command(BaseCommand):
    help = "Import fuel stations from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to CSV file"
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        FuelStation.objects.all().delete()

        stations = []

        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                station = FuelStation(
                    opis_id=row["OPIS Truckstop ID"],
                    name=row["Truckstop Name"],
                    address=row["Address"],
                    city=row["City"],
                    state=row["State"],
                    rack_id=row["Rack ID"],
                    retail_price=Decimal(
                        row["Retail Price"]
                    ),
                )

                stations.append(station)

        FuelStation.objects.bulk_create(
            stations,
            batch_size=1000
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(stations)} fuel stations."
            )
        )