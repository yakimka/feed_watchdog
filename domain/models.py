import dataclasses


@dataclasses.dataclass()
class Source:
    id: int
    name: str
    slug: str
    url: str
    parser_type: str
    encoding: str = ""
    description: str = ""
    tags: tuple | list = ()


@dataclasses.dataclass()
class Receiver:
    id: int
    name: str
    slug: str
    type: str
    recipient: str
    message_template: str


@dataclasses.dataclass()
class Stream:
    id: int
    source: Source
    receiver: Receiver
    message_template: str = ""
