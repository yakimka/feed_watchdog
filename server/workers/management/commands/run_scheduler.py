import asyncio
import logging
from contextlib import suppress
from functools import partial

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand

from db.models import Interval
from service_layer.collector import Collector

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs the scheduler"

    def handle(self, *args, **options):
        logger.info("Starting scheduler")
        scheduler = AsyncIOScheduler()
        add_interval_jobs(scheduler)
        scheduler.add_job(
            update_jobs, "interval", [scheduler, get_context()], seconds=60
        )
        scheduler.start()

        with suppress(KeyboardInterrupt):
            asyncio.get_event_loop().run_forever()


def get_context():
    streams_count = Interval.objects.count()
    updated_at = Interval.objects.order_by("-updated")[0].updated

    return {
        "streams_count": streams_count,
        "updated_at": updated_at,
    }


def update_jobs(scheduler, context: dict):
    new_context = get_context()
    if context == new_context:
        return

    logger.info("Updating jobs")
    context.update(new_context)
    for job in scheduler.get_jobs():
        if job.name != "update_jobs":
            job.remove()
    add_interval_jobs(scheduler)


def add_interval_jobs(scheduler):
    for interval in Interval.objects.all():
        collect = partial(collect_streams, interval.cron)
        scheduler.add_job(
            collect,
            CronTrigger.from_crontab(interval.cron),
            replace_existing=True,
        )


async def collect_streams(cron_interval: str):
    logger.info("Collecting streams for %s", cron_interval)
    collector = Collector()
    await collector.send_events(cron_interval=cron_interval)
