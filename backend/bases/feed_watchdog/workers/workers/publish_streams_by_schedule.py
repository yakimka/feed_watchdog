import asyncio
import logging
from functools import partial
from typing import Iterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dependency_injector.wiring import Provide, inject

from feed_watchdog.api_client.client import FeedWatchdogAPIClient
from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.domain.events import ProcessStreamEvent
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.workers.container import Container
from feed_watchdog.workers.settings import Settings

logger = logging.getLogger(__name__)


class ProcessStreamsByScheduleWorker(BaseCommand):
    def handle(self, args):  # noqa: U100
        loop = asyncio.new_event_loop()
        loop.create_task(self._run_scheduler())
        try:
            loop.run_forever()
        finally:
            loop.close()

    async def _run_scheduler(self):
        logger.info("Starting scheduler")
        scheduler = AsyncIOScheduler()
        await add_interval_jobs(scheduler)
        scheduler.start()


@inject
async def add_interval_jobs(
    scheduler: AsyncIOScheduler,
    api_client: FeedWatchdogAPIClient = Provide[
        Container.feed_watchdog_api_client
    ],
) -> None:
    for interval in await api_client.get_intervals():
        collect = partial(collect_and_publish_streams, interval)
        scheduler.add_job(
            collect,
            CronTrigger.from_crontab(interval),
            name=f"collect_and_publish_streams_{interval}",
            replace_existing=True,
        )


@inject
async def collect_and_publish_streams(
    cron_interval: str,
    api_client: FeedWatchdogAPIClient = Provide[
        Container.feed_watchdog_api_client
    ],
    settings: Settings = Provide[Container.settings],
):
    logger.info("Collecting streams for %s", cron_interval)
    streams = await api_client.get_streams(interval=cron_interval)
    await send_events(
        settings.app.streams_topic,
        (ProcessStreamEvent.from_dict(stream.dict()) for stream in streams),
    )


@inject
async def send_events(
    topic_name,
    events: Iterable[ProcessStreamEvent],
    publisher: Publisher = Provide[Container.publisher],
):
    i = 0
    for i, event in enumerate(events, start=1):  # noqa: B007
        await publisher.publish(topic_name, event.as_dict())
    logger.info("Sent %s events", i)
