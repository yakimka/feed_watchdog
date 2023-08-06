import dataclasses
import logging
from functools import lru_cache
from typing import Iterable

from aiogram import Bot

from feed_watchdog.domain.models import Post
from feed_watchdog.handlers import HandlerOptions, HandlerType, register_handler
from feed_watchdog.synchronize.lock import async_lock
from feed_watchdog.text import template_to_text

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TelegramBotOptions(HandlerOptions):
    DESCRIPTIONS = {
        "chat_id": ("Chat ID", "Telegram chat id"),
        "disable_link_preview": ("Disable link preview", ""),
    }

    chat_id: str
    disable_link_preview: bool = False


@lru_cache(maxsize=128)
def _get_bot(token: str) -> Bot:
    return Bot(token=token)


@register_handler(
    type=HandlerType.receivers.value,
    name="telegram_bot",
    options=TelegramBotOptions,
)
class TelegramBot:
    MAX_MESSAGE_LENGTH = 4096
    MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20
    pause_between_send = 60 / MAX_MESSAGES_PER_MINUTE_PER_GROUP  # seconds

    def __init__(self, name: str, token: str):
        self._name = name
        self.bot = _get_bot(token)

    def _lock_key(self, *_, **__):
        return self._name

    async def __call__(
        self,
        posts: Iterable[Post],
        *,
        template: str,
        squash: bool = False,
        options: TelegramBotOptions,
    ) -> None:
        if squash:
            await self._send_squashed_message(
                posts,
                template=template,
                options=options,
            )
        else:
            await self._send_separate_messages(
                posts,
                template=template,
                options=options,
            )

    async def _send_separate_messages(
        self,
        posts: Iterable[Post],
        *,
        template: str,
        options: TelegramBotOptions,
    ) -> None:
        for post in posts:
            message = template_to_text(template, **post.template_kwargs())
            await self._send_message(
                message=message,
                chat_id=options.chat_id,
                disable_link_preview=options.disable_link_preview,
            )

    async def _send_squashed_message(  # noqa C901
        self,
        posts: Iterable[Post],
        *,
        template: str,
        options: TelegramBotOptions,
    ) -> None:
        posts = list(posts)
        if not posts:
            return
        parts: list[str] = []
        delimiter = "\n-----\n"
        for post in posts:
            message = template_to_text(template, **post.template_kwargs())
            parts.extend((message.strip(), delimiter))
        if parts:
            parts.pop()

        added_truncated_message = False
        while sum(len(part) for part in parts) > self.MAX_MESSAGE_LENGTH:
            if not added_truncated_message:
                parts.append("\nTruncated...")
                added_truncated_message = True
            parts.pop(-2)

        message = "".join(parts)
        await self._send_message(
            message=message,
            chat_id=options.chat_id,
            disable_link_preview=options.disable_link_preview,
        )

    @async_lock(key=_lock_key, wait_time=pause_between_send)
    async def _send_message(
        self, message: str, chat_id: str, disable_link_preview: bool
    ) -> None:
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=disable_link_preview,
        )
        logger.info("Sent post to %s (%s)", self._name, chat_id)
