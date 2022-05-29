from typing import Protocol


class Post(Protocol):
    post_id: str
    source_tags: list | tuple

    def template_kwargs(self) -> dict:
        pass

    @classmethod
    def fields_schema(cls) -> dict:
        pass
