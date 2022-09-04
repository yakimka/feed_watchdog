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


class Modifier(BaseModel):
    type: str
    options: dict


class Stream(BaseModel):
    source: Source
    receiver: Receiver
    slug: str
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[Modifier] = []
