import dataclasses


@dataclasses.dataclass()
class Source:
    name: str
    slug: str
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    description: str = ""
    tags: tuple | list = ()


@dataclasses.dataclass()
class Receiver:
    name: str
    slug: str
    type: str
    options: dict
    message_template: str


@dataclasses.dataclass()
class Filter:
    type: str
    options: dict


@dataclasses.dataclass()
class Stream:
    uid: str
    source: Source
    receiver: Receiver
    squash: bool
    message_template: str = ""
    filters: list[Filter] = dataclasses.field(default_factory=list)
