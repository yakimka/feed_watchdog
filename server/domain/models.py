import dataclasses

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    pass


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


@dataclasses.dataclass()
class Modifier:
    type: str
    options: dict


@dataclasses.dataclass()
class Stream:
    uid: str
    source: Source
    receiver: Receiver
    squash: bool
    receiver_options_override: dict
    message_template: str = ""
    modifiers: list[Modifier] = dataclasses.field(default_factory=list)
