import dataclasses
from typing import Protocol

from dacite import from_dict
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    pass


class User(BaseModel):
    id: str
    email: str


class UserInDB(User):
    password: str


class RefreshToken(BaseModel):
    token: str
    user_id: str


class Source(BaseModel):
    name: str
    slug: str
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    description: str = ""
    tags: list = []


class Receiver(BaseModel):
    name: str
    slug: str
    type: str
    options: dict
    options_allowed_to_override: list[str] = []


class Modifier(BaseModel):
    type: str
    options: dict


class BaseStream(BaseModel):
    slug: str
    intervals: list[str]
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[Modifier] = []
    active: bool


class Stream(BaseStream):
    source_slug: str
    receiver_slug: str


class StreamWithRelations(Stream):
    source: Source
    receiver: Receiver


@dataclasses.dataclass()
class Post(Protocol):
    post_id: str
    source_tags: tuple | list

    def template_kwargs(self) -> dict:
        raise NotImplementedError

    @classmethod
    def fields_schema(cls) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict):
        return from_dict(cls, data=data)
