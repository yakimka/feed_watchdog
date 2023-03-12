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
