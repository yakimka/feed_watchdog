from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Sequence

from tldextract import tldextract

if TYPE_CHECKING:
    from . import events, models


def mutate_posts_with_stream_data(
    stream: events.ProcessStreamEvent,
    posts: Sequence[models.Post],
) -> None:
    for post in posts:
        post.post_id = _generate_post_id(post.post_id)
        post.message_template = stream.message_template
        post.source_tags = stream.source_tags


def _generate_post_id(post_id: str) -> str:
    return post_id.removeprefix("https://").removeprefix("http://")


@lru_cache(maxsize=None)
def domain_from_url(url: str):
    _, td, tsu = tldextract.extract(url)
    return f"{td}.{tsu}"
