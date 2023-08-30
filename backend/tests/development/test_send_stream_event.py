import json
from unittest.mock import AsyncMock, Mock

import pytest

from development import send_stream_event
from feed_watchdog.api_client.client import (
    FeedWatchdogAPIClient,
    ReceiverResp,
    SourceResp,
    StreamResp,
)

pytestmark = pytest.mark.usefixtures(
    "_mock_feed_watchdog_api_client", "redis_pubsub_server"
)


@pytest.fixture()
def stream() -> StreamResp:
    return StreamResp(
        slug="source-to-receiver",
        intervals=["*/5 * * * *"],
        squash=True,
        receiver_options_override={},
        message_template="Url: $url",
        modifiers=[],
        active=True,
        source=SourceResp(
            name="Source",
            slug="source",
            fetcher_type="text",
            fetcher_options={"url": "https://example.com/rss"},
            parser_type="rss",
            parser_options={},
            description="Source description",
            tags=["tag1", "tag2"],
        ),
        receiver=ReceiverResp(
            name="Receiver",
            slug="receiver",
            type="telegram",
            options={"chat_id": 123},
            options_allowed_to_override=[],
        ),
    )


@pytest.fixture()
def feed_watchdog_api_client(stream) -> FeedWatchdogAPIClient:
    return Mock(
        spec_set=FeedWatchdogAPIClient,
        get_stream=AsyncMock(return_value=stream),
    )


@pytest.fixture()
def _mock_feed_watchdog_api_client(monkeypatch, feed_watchdog_api_client):
    monkeypatch.setattr(
        send_stream_event,
        "get_feed_watchdog_api_client",
        lambda *args, **kwargs: feed_watchdog_api_client,
    )


@pytest.fixture()
def argv(redis_pubsub_server_url) -> dict[str, str]:
    return {
        "--stream-slug": "guido-van-rossum-blog-to-my-feed-telegram",
        "--api-token": "my_token",
        "--api-url": "http://localhost:8000/api",
        "--redis-pubsub-url": redis_pubsub_server_url,
    }


def make_argv_list(argv):
    return [""] + [f"{k}={v}" for k, v in argv.items()]


@pytest.fixture()
def get_messages(redis_pubsub_server):
    async def get_messages():
        result = await redis_pubsub_server.xread(
            {send_stream_event.STREAMS_TOPIC: "0-0"}, count=10
        )
        messages = []
        for _, stream in result:
            for _, message in stream:
                messages.append({k: json.loads(v) for k, v in message.items()})
        return messages

    return get_messages


async def test_send_events(argv, get_messages):
    await send_stream_event.main(make_argv_list(argv))

    result = await get_messages()

    assert len(result) == 1
    event = result[0]
    assert event == {
        "__event_name__": "ProcessStreamEvent",
        "slug": "source-to-receiver",
        "message_template": "Url: $url",
        "squash": True,
        "modifiers": [],
        "source": {
            "fetcher_type": "text",
            "fetcher_options": {"url": "https://example.com/rss"},
            "parser_type": "rss",
            "parser_options": {},
            "tags": ["tag1", "tag2"],
        },
    }


async def test_get_token_from_env(argv, monkeypatch):
    monkeypatch.setenv(name="MY_TOKEN", value="my_secret_token")
    argv["--api-token"] = "ENV:MY_TOKEN"
    mock_get_httpx_stream_client = Mock()
    monkeypatch.setattr(
        send_stream_event,
        "get_httpx_stream_client",
        mock_get_httpx_stream_client,
    )

    await send_stream_event.main(make_argv_list(argv))

    args = mock_get_httpx_stream_client.call_args.args
    assert args == ("my_secret_token",)


async def test_get_token_from_env_raise_error_if_env_not_set(argv):
    argv["--api-token"] = "ENV:MY_TOKEN"

    with pytest.raises(ValueError, match="MY_TOKEN not found"):
        await send_stream_event.main(make_argv_list(argv))
