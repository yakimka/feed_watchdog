from __future__ import annotations

import dataclasses
import json
import logging
from typing import IO, TYPE_CHECKING, Callable, Iterable, Protocol

from processors.adapters.error_tracking import write_warn_message
from processors.adapters.fetch import fetch_text_from_url
from processors.domain.logic import mutate_posts_with_stream_data
from processors.handlers import (
    get_parser_by_name,
    get_receiver_by_name,
    get_registered_handlers,
)

if TYPE_CHECKING:
    from processors.domain import events, models
    from processors.storage import Storage


logger = logging.getLogger(__name__)


async def process_stream(
    event: events.ProcessStreamEvent, storage: Storage
) -> None:
    text = await fetch_text_from_url(
        event.source_url, encoding=event.source_encoding, retry=2
    )
    if not text:
        return None
    parser = get_parser_by_name(event.source_parser_type)
    posts = await parser(text)
    if not posts:
        write_warn_message(
            f"Can't find posts for {event.source_url}", logger=logger
        )
    mutate_posts_with_stream_data(event, posts)
    # TODO posts = apply_filters(posts)

    await send_new_posts_to_receiver(reversed(posts), event, storage)


class Receiver(Protocol):
    async def send(self, post: models.Post) -> None:
        pass


async def send_new_posts_to_receiver(
    posts: Iterable[models.Post],
    event: events.ProcessStreamEvent,
    storage: Storage,
) -> None:
    receiver = get_receiver_by_name(
        event.receiver_type, options=event.receiver_options
    )

    is_init = (
        await storage.sent_posts_count(event.uid, event.receiver_type) == 0
    )
    for post in posts:
        if is_init:
            await storage.save_post_sent_flag(
                post.post_id, event.uid, event.receiver_type
            )
        elif not await storage.post_was_sent(
            post.post_id, event.uid, event.receiver_type
        ):
            await receiver(post)
            await storage.save_post_sent_flag(
                post.post_id, event.uid, event.receiver_type
            )


@dataclasses.dataclass
class Configuration:
    pass


def parse_configuration() -> dict:
    handlers = get_registered_handlers()
    return {
        "handlers": {
            "parsers": [
                {
                    "type": name,
                    "options": dict(opt.to_json_schema()) if opt else {},
                }
                for name, _, opt in handlers["parsers"].values()
            ],
            "receivers": [
                {
                    "type": name,
                    "options": dict(opt.to_json_schema()) if opt else {},
                }
                for name, _, opt in handlers["receivers"].values()
            ],
        }
    }


def write_configuration(
    fp: IO[str], parser: Callable[[], dict] = parse_configuration
):
    json.dump(parser(), fp, indent=2)
