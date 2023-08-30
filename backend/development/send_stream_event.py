import argparse
import asyncio
import os
import sys

import httpx
from redis import asyncio as aioredis

from feed_watchdog.api_client.client import FeedWatchdogAPIClient
from feed_watchdog.domain.events import ProcessStreamEvent
from feed_watchdog.pubsub.publisher import Publisher

STREAMS_TOPIC: str = "feed_watchdog:streams"


def get_httpx_stream_client(token: str, timeout: int = 5) -> httpx.AsyncClient:
    headers = {"Authorization": f"Bearer {token}"}
    return httpx.AsyncClient(headers=headers, timeout=timeout)


def get_feed_watchdog_api_client(http_client: httpx.AsyncClient, base_url: str):
    return FeedWatchdogAPIClient(http_client, base_url=base_url)


async def send_stream_event(
    topic_name,
    stream_slug: str,
    api_client: FeedWatchdogAPIClient,
    publisher: Publisher,
) -> None:
    stream = await api_client.get_stream(slug=stream_slug)
    if stream is None:
        raise ValueError(f"Stream {stream_slug} not found")
    event = ProcessStreamEvent.from_dict(stream.dict())
    await publisher.publish(topic_name, event.as_dict())


async def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-token", required=True)
    parser.add_argument("--stream-slug", required=True)
    parser.add_argument("--api-url", default="http://feed_watchdog_api:8000/api")
    parser.add_argument("--redis-pubsub-url", default="redis://redis:6379/2")
    args = parser.parse_args(argv[1:])
    if args.api_token.startswith("ENV:"):
        try:
            args.api_token = os.environ[args.api_token[4:]].strip()
        except KeyError:
            raise ValueError(
                f"Environment variable {args.api_token[4:]} not found"
            ) from None

    http_client = get_httpx_stream_client(args.api_token)
    api_client = get_feed_watchdog_api_client(http_client, base_url=args.api_url)
    redis_client = aioredis.from_url(args.redis_pubsub_url, decode_responses=True)
    publisher = Publisher(redis_client)
    await send_stream_event(
        topic_name=STREAMS_TOPIC,
        stream_slug=args.stream_slug,
        api_client=api_client,
        publisher=publisher,
    )


if __name__ == "__main__":
    asyncio.run(main(sys.argv))
