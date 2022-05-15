import asyncio
import json
import logging

import feedparser

from processors.domain import models
from processors.handlers import register_parser

logger = logging.getLogger(__name__)


@register_parser()
async def rss(text: str) -> list[models.Post]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _handler, text)


def _handler(text: str) -> list[models.Post]:
    posts: list[models.Post] = []

    if not text:
        return posts

    def get_tags(entry):
        return tuple(tag.term for tag in entry.get("tags", []))

    feed = feedparser.parse(
        text, response_headers={"content-type": "text/html; charset=utf-8"}
    )
    for entry in feed["entries"]:
        try:
            id_field = entry.keymap["guid"]
            posts.append(
                models.Post(
                    post_id=entry.get(id_field),
                    title=entry.title,
                    url=entry.get("link"),
                    post_tags=get_tags(entry),
                    raw=json.loads(json.dumps(entry)),
                ),
            )
        except Exception:  # noqa: PLW0703, PIE786
            entry = json.dumps(entry, sort_keys=True, indent=4)
            logger.exception("Failed to parse entry: %s", entry)

    return posts
