from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Protocol

from processors.adapters.error_tracking import write_warn_message
from processors.adapters.fetch import fetch_text_from_url
from processors.domain.logic import mutate_posts_with_stream_data
from processors.handlers import get_parser_by_name, get_receiver_by_name

if TYPE_CHECKING:
    from processors.domain import events, models
    from processors.storage import Storage


async def process_stream(
    event: events.ProcessStreamEvent, storage: Storage
) -> None:
    text = await fetch_text_from_url(
        event.source_url, encoding=event.source_encoding
    )
    parser = get_parser_by_name(event.source_parser_type)
    posts = await parser(text)
    if not posts:
        write_warn_message(f"Can't find posts for {event.source_url}")
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
    receiver = get_receiver_by_name(event.receiver_type)

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
            await receiver.send(post, chat_id=event.receiver_recipient)
            await storage.save_post_sent_flag(
                post.post_id, event.uid, event.receiver_type
            )
