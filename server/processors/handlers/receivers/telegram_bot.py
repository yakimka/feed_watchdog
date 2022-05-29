from __future__ import annotations

import dataclasses
import logging
from typing import TYPE_CHECKING

from aiogram import Bot

from processors.adapters.lock import async_lock
from processors.domain.logic import make_message_from_template
from processors.handlers import HandlerOptions, HandlerType, register_handler

if TYPE_CHECKING:
    from processors.domain.models import Post

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TelegramBotOptions(HandlerOptions):
    DESCRIPTIONS = {
        "chat_id": ("Chat ID", "Telegram chat id"),
        "disable_link_preview": ("Disable link preview", ""),
    }

    chat_id: str
    disable_link_preview: bool = False


@register_handler(
    type=HandlerType.receivers.value,
    name="telegram_bot",
    options=TelegramBotOptions,
)
class TelegramBot:
    MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20
    pause_between_send = 60 / MAX_MESSAGES_PER_MINUTE_PER_GROUP  # seconds

    def __init__(self, name: str, token: str):
        self._name = name
        self._token = token
        self.bot = Bot(token=self._token)

    def _lock_key(self, *_, **__):
        return self._name

    @async_lock(key=_lock_key, wait_time=pause_between_send)
    async def __call__(
        self,
        post: Post,
        template: str,
        *,
        options: TelegramBotOptions,
    ) -> None:
        await self.bot.send_message(
            chat_id=options.chat_id,
            text=make_message_from_template(template, **post.template_kwargs()),
            parse_mode="HTML",
            disable_web_page_preview=options.disable_link_preview,
        )
        logger.info("Sent post to %s (%s)", self._name, options.chat_id)
