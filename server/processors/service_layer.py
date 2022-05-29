from __future__ import annotations

import json
import logging
from typing import IO, TYPE_CHECKING, Callable, Iterable

from processors.adapters.error_tracking import write_warn_message
from processors.domain.logic import mutate_posts_with_stream_data
from processors.handlers import (
    HandlerType,
    get_handler_by_name,
    get_registered_handlers,
)

if TYPE_CHECKING:
    from processors.domain import events, models
    from processors.storage import Storage


logger = logging.getLogger(__name__)


async def process_stream(
    event: events.ProcessStreamEvent, storage: Storage
) -> None:
    fetcher = get_handler_by_name(
        type=HandlerType.fetchers.value,
        name=event.source_fetcher_type,
        options=event.source_fetcher_options,
    )
    text = await fetcher()
    if not text:
        return None
    parser = get_handler_by_name(
        name=event.source_parser_type,
        type=HandlerType.parsers.value,
        options=event.source_parser_options,
    )
    posts = await parser(text)
    if not posts:
        write_warn_message(f"Can't find posts for {event.uid}", logger=logger)
    mutate_posts_with_stream_data(event, posts)
    # TODO posts = apply_filters(posts)

    await send_new_posts_to_receiver(reversed(posts), event, storage)


async def send_new_posts_to_receiver(
    posts: Iterable[models.Post],
    event: events.ProcessStreamEvent,
    storage: Storage,
) -> None:
    receiver = get_handler_by_name(
        name=event.receiver_type,
        type=HandlerType.receivers.value,
        options=event.receiver_options,
    )

    is_init = (
        await storage.sent_posts_count(event.uid, event.receiver_type) == 0
    )
    if is_init:
        write_warn_message(
            f"Empty database for {event.uid} {event.receiver_type}",
            logger=logger,
        )
    new_posts = 0
    for post in posts:
        if is_init:
            await storage.save_post_sent_flag(
                post.post_id, event.uid, event.receiver_type
            )
        elif not await storage.post_was_sent(
            post.post_id, event.uid, event.receiver_type
        ):
            await receiver(post, template=event.message_template)
            await storage.save_post_sent_flag(
                post.post_id, event.uid, event.receiver_type
            )
            new_posts += 1
    if new_posts:
        msg = (
            f"{new_posts} new posts sent to {event.receiver_type} ({event.uid})"
        )
    else:
        msg = f"No new posts sent to {event.receiver_type} ({event.uid})"

    logger.info(msg)


def parse_configuration() -> dict:
    handlers = get_registered_handlers()
    results: dict = {"handlers": {}}

    for item in HandlerType:
        results["handlers"][item.value] = [
            {
                "type": name,
                "options": dict(opt.to_json_schema()) if opt else {},
                "return_fields_schema": f_schema,
            }
            for name, _, opt, f_schema in handlers[item.value].values()
        ]

    return results


def write_configuration(
    fp: IO[str], parser: Callable[[], dict] = parse_configuration
):
    json.dump(parser(), fp, indent=2)
