import re
import string
from functools import lru_cache
from typing import Iterable, Sequence

from tldextract import tldextract

from . import events, models


def mutate_posts_with_stream_data(
    stream: events.ProcessStreamEvent,
    posts: Sequence[models.Post],
) -> None:
    for post in posts:
        post.post_id = _generate_post_id(post.post_id)
        post.source_tags = stream.source.tags


def _generate_post_id(post_id: str) -> str:
    return post_id.removeprefix("https://").removeprefix("http://")


@lru_cache(maxsize=None)
def domain_from_url(url: str):
    _, td, tsu = tldextract.extract(url)
    return f"{td}.{tsu}"


only_letters_and_underscore = re.compile(r"[^a-zA-Zа-яА-Я0-9_ёЁіІїЇґҐєЄ]")
multiple_underscores = re.compile(r"_+")


def make_hash_tags(tags: Iterable[str]) -> list[str]:
    hash_tags = []
    for tag in tags:
        hash_tag = re.sub(only_letters_and_underscore, "_", tag)
        hash_tag = re.sub(multiple_underscores, "_", hash_tag)
        hash_tags.append(f"#{hash_tag.lower()}")
    return hash_tags


def make_message_from_template(template_string: str, **kwargs) -> str:
    template = string.Template(template_string)
    return template.safe_substitute(kwargs)
