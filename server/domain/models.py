import dataclasses


@dataclasses.dataclass()
class Source:
    name: str
    slug: str
    url: str
    parser_type: str
    encoding: str = ""
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
class Stream:
    uid: str
    source: Source
    receiver: Receiver
    message_template: str = ""
