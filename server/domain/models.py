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
    options_allowed_to_override: list[str]


class Modifier(BaseModel):
    type: str
    options: dict


class Stream(BaseModel):
    name: str
    source: Source
    receiver: Receiver
    slug: str
    squash: bool
    receiver_options_override: dict
    message_template: str
    modifiers: list[Modifier] = []
