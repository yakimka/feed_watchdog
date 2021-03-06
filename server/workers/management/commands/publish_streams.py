import asyncio

from django.core.management.base import BaseCommand

from service_layer.collector import Collector


class Command(BaseCommand):
    help = "Publish streams"

    def handle(self, *args, **options):
        collector = Collector()

        asyncio.run(collector.send_events())
