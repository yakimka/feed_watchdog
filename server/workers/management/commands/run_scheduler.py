import asyncio
from contextlib import suppress

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand

from service_layer.collector import Collector


class Command(BaseCommand):
    help = "Runs the scheduler"

    def handle(self, *args, **options):
        collector = Collector()
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            collector.send_events,
            CronTrigger.from_crontab("* * * * *"),
        )
        scheduler.start()

        with suppress(KeyboardInterrupt):
            asyncio.get_event_loop().run_forever()
