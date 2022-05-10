import dataclasses
import re
from typing import Iterable

only_letters_and_underscore = re.compile(r"[^a-zA-Zа-яА-Я0-9_ёЁіІїЇґҐєЄ]")
multiple_underscores = re.compile(r"_+")


@dataclasses.dataclass()
class Post:
    post_id: str
    title: str
    url: str
    post_tags: tuple
    raw: dict
    message_template: str = ""
    source_tags: tuple | list = ()

    def template_kwargs(self):
        return {
            "post_id": self.post_id,
            "title": self.title,
            "url": self.url,
            "post_tags": "; ".join(self.post_tags),
            "source_tags": "; ".join(self.source_tags),
            "post_hash_tags": " ".join(self.make_hash_tags(self.post_tags)),
            "source_hash_tags": " ".join(self.make_hash_tags(self.source_tags)),
        }

    @staticmethod
    def make_hash_tags(tags: Iterable[str]) -> list[str]:
        hash_tags = []
        for tag in tags:
            hash_tag = re.sub(only_letters_and_underscore, "_", tag)
            hash_tag = re.sub(multiple_underscores, "_", hash_tag)
            hash_tags.append(f"#{hash_tag.lower()}")
        return hash_tags
