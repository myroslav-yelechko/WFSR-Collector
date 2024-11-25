from django.core.management.base import BaseCommand

from collector.jobs.collect_forecast import job as collect_forecast

class Command(BaseCommand):
    help = 'Invoke cron-job "collect_forecast"'

    def add_arguments(self, parser):
        parser.add_argument(
            "--lt",
            action="store_true",
            help="Argument for limiting the number of settlements for which to collect data in tests",
        )

    def handle(self, *args, **options):
        if options.get("lt"):
            return collect_forecast(options.get("lt"))
        return collect_forecast()