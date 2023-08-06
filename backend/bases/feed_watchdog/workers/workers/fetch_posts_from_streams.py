import asyncio
import logging
import uuid
from dataclasses import asdict
from typing import Iterable, Sequence

from dependency_injector.wiring import Provide, inject

from feed_watchdog.commands.core import BaseCommand
from feed_watchdog.domain.events import PostParsed, ProcessStreamEvent
from feed_watchdog.domain.models import Post
from feed_watchdog.handlers import HandlerType, get_handler_by_name
from feed_watchdog.pubsub.publisher import Publisher
from feed_watchdog.repositories.post import RedisPostRepository
from feed_watchdog.sentry.error_tracking import write_warn_message
from feed_watchdog.workers.container import Container, container
from feed_watchdog.workers.settings import Settings

logger = logging.getLogger(__name__)


class ProcessStreamsByScheduleWorker(BaseCommand):
    @inject
    def setup(
        self,
        settings: Settings = Provide[Container.settings],
        post_repository: RedisPostRepository = Provide[
            Container.post_repository
        ],
        publisher: Publisher = Provide[Container.publisher],
    ):
        self._settings = settings
        self._post_repository = post_repository
        self._publisher = publisher
        self._subscriber = container.subscriber(
            topic_name=self._settings.app.streams_topic,
            group_id="fetch_posts_from_streams",
            consumer_id=uuid.uuid4().hex,
        )

    def handle(self, args):
        asyncio.run(self.process_streams(), debug=True)

    @inject
    async def process_streams(self) -> None:
        async for msg_id, msg_data in self._subscriber:
            event = ProcessStreamEvent.from_dict(msg_data)
            text = await self.fetch_text(event)
            if not text:
                return None

            posts = await self.parse_posts(event, text)
            if not posts:
                return None

            final_posts = await self.apply_modifiers_to_posts(
                event.modifiers, posts
            )
            events_for_sending = await self.parse_new_events(event, final_posts)
            await self.send_events(events_for_sending)

            left_posts = {post.post_id for post in posts} - {
                event.post.post_id for event in events_for_sending
            }
            if left_posts:
                await self._post_repository.mark_post_as_seen(
                    event.slug, *left_posts
                )

            await self._subscriber.commit(msg_id)

    async def fetch_text(self, event) -> str | None:
        fetcher = get_handler_by_name(
            type=HandlerType.fetchers.value,
            name=event.source.fetcher_type,
            options=event.source.fetcher_options,
        )
        text = await fetcher()
        if not text:
            write_warn_message(
                f"Can't fetch text for {event.slug}", logger=logger
            )
        return text

    async def parse_posts(self, event, text) -> list[Post]:
        parser = get_handler_by_name(
            name=event.source.parser_type,
            type=HandlerType.parsers.value,
            options=event.source.parser_options,
        )
        posts = await parser(text)
        if not posts:
            write_warn_message(
                f"Can't find posts for {event.slug}", logger=logger
            )
        mutate_posts_with_stream_data(event, posts)
        return posts

    async def apply_modifiers_to_posts(
        self, modifiers: list, posts: Iterable[Post]
    ) -> list[Post]:
        for modifier in modifiers:
            modifier_func = get_handler_by_name(
                name=modifier.type,
                type=HandlerType.modifiers.value,
                options=modifier.options,
            )
            posts = await modifier_func(posts)
        return posts

    async def parse_new_events(self, event, posts) -> list[PostParsed]:
        events_for_sending = []
        is_first_run = bool(
            await self._post_repository.seen_posts_count(stream_id=event.slug)
        )
        for post in reversed(posts):
            if is_first_run:
                write_warn_message(f"First run for {event.slug}", logger=logger)
                break
            if await self._post_repository.is_post_seen(
                post.post_id, stream_id=event.slug
            ):
                continue

            events_for_sending.append(
                PostParsed(
                    stream_slug=event.slug,
                    post=post,
                )
            )
        return events_for_sending

    async def send_events(self, events_for_sending) -> None:
        for event in events_for_sending:
            await self._publisher.publish(
                self._settings.app.post_parsed_topic, data=asdict(event)
            )
            await self._post_repository.mark_post_as_seen(
                event.stream_slug, event.post.post_id
            )


def mutate_posts_with_stream_data(
    stream: ProcessStreamEvent,
    posts: Sequence[Post],
) -> None:
    for post in posts:
        post.post_id = _clean_post_id(post.post_id)
        post.source_tags = stream.source.tags


def _clean_post_id(post_id: str) -> str:
    return post_id.removeprefix("https://").removeprefix("http://")
