import asyncio
import logging
import os
from functools import partial
from typing import Iterable

import httpx
import sentry_sdk
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel
from sentry_sdk.integrations.logging import LoggingIntegration

from adapters.publisher import Publisher
from app_settings import Topic
from container import Container, container, wire_modules
from domain.events import ProcessStreamEvent

logger = logging.getLogger(__name__)


def get_client() -> httpx.AsyncClient:
    transport = httpx.AsyncHTTPTransport(retries=2)
    token = os.environ["SCHEDULER_FW_API_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.AsyncClient(headers=headers, transport=transport, timeout=30)


class SourceResp(BaseModel):
    name: str
    slug: str
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    description: str
    tags: list


class ReceiverResp(BaseModel):
    name: str
    slug: str
    type: str
    options: dict
    options_allowed_to_override: list[str]


class ModifierResp(BaseModel):
    type: str
    options: dict


class StreamResp(BaseModel):
    slug: str
    intervals: list[str]
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[ModifierResp]
    active: bool
    source: SourceResp
    receiver: ReceiverResp


class StreamClientError(Exception):
    pass


class HTTPXStreamClient:
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url.removesuffix("/")

    async def get_streams(self, interval: str) -> list[StreamResp]:
        result: list[StreamResp] = []
        has_next = True
        page = 1
        while has_next:
            try:
                has_next, streams = await self._get_streams(
                    interval=interval, page=page
                )
            except httpx.HTTPError as e:
                raise StreamClientError("Error while fetching streams") from e
            page += 1
            result.extend(streams)
        return result

    async def _get_streams(
        self, interval: str, page=1, page_size=300
    ) -> tuple[bool, list[StreamResp]]:
        response = await self._client.get(
            f"{self._base_url}/streams",
            params={
                "active": True,
                "page": page,
                "page_size": page_size,
                "interval": interval,
            },
        )
        response.raise_for_status()
        result = response.json()
        has_next = result["count"] > page * page_size
        return has_next, [
            StreamResp.parse_obj(stream) for stream in result["results"]
        ]

    async def get_intervals(self) -> list[str]:
        response = await self._client.get(f"{self._base_url}/streams/intervals")
        response.raise_for_status()
        return [item["value"] for item in response.json()]


class Command:
    help = "Runs the scheduler"

    async def handle(self, stream_client: HTTPXStreamClient):
        logger.info("Starting scheduler")
        scheduler = AsyncIOScheduler()
        await add_interval_jobs(scheduler, stream_client=stream_client)
        scheduler.add_job(
            update_jobs,
            "interval",
            [scheduler, stream_client, get_context()],
            seconds=60,
        )
        scheduler.start()


def get_context() -> dict:
    return {
        "streams_count": None,
        "updated_at": None,
    }


async def update_jobs(
    scheduler, stream_client: HTTPXStreamClient, context: dict
):
    new_context = get_context()
    if context == new_context:
        return

    logger.info("Updating jobs")
    context.update(new_context)
    for job in scheduler.get_jobs():
        if job.name != "update_jobs":
            job.remove()
    await add_interval_jobs(scheduler, stream_client=stream_client)


async def add_interval_jobs(
    scheduler: AsyncIOScheduler, stream_client: HTTPXStreamClient
) -> None:
    for interval in await stream_client.get_intervals():
        collect = partial(collect_and_publish_streams, interval, stream_client)
        scheduler.add_job(
            collect,
            CronTrigger.from_crontab(interval),
            replace_existing=True,
        )


async def send_events(events: Iterable[ProcessStreamEvent]):
    i, publisher = 0, container.publisher()
    for i, event in enumerate(events, start=1):
        await publisher.publish(Topic.STREAMS.value, event)
    logger.info("Sent %s events", i)


async def collect_and_publish_streams(
    cron_interval: str, stream_client: HTTPXStreamClient
):
    logger.info("Collecting streams for %s", cron_interval)
    streams = await stream_client.get_streams(interval=cron_interval)
    await send_events(
        ProcessStreamEvent.from_dict(stream.dict()) for stream in streams
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if sentry_dsn := os.environ.get("SENTRY_DSN"):
        sentry_logging = LoggingIntegration(
            level=logging.INFO, event_level=logging.ERROR
        )
        sentry_sdk.init(dsn=sentry_dsn, integrations=[sentry_logging])

    httpx_client = get_client()
    stream_client = HTTPXStreamClient(
        httpx_client, "http://feed_watchdog:8000/api"
    )

    loop = asyncio.get_event_loop()
    loop.create_task(Command().handle(stream_client=stream_client))
    try:
        loop.run_forever()
    finally:
        loop.close()
