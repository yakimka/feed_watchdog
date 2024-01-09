import dataclasses
from typing import Any

from dacite import from_dict


@dataclasses.dataclass
class Event:
    def as_dict(self) -> dict:
        data = dataclasses.asdict(self)
        data["__event_name__"] = type(self).__name__
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return from_dict(data_class=cls, data=data)


def parse_event(message: dict[str, Any]) -> Event:
    event_class = globals()[message.pop("__event_name__")]
    return event_class.from_dict(data=message)


@dataclasses.dataclass
class SourceData:
    fetcher_type: str
    fetcher_options: dict
    parser_type: str
    parser_options: dict
    tags: list


@dataclasses.dataclass
class ReceiverData:
    type: str
    options: dict


@dataclasses.dataclass
class ModifierData:
    type: str
    options: dict


@dataclasses.dataclass
class ProcessStreamEvent(Event):
    slug: str
    message_template: str
    squash: bool
    modifiers: list[ModifierData]
    source: SourceData


@dataclasses.dataclass
class Message:
    post_id: str
    text: str
    template: str = ""
    template_kwargs: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class MessageBatch(Event):
    stream_slug: str
    messages: list[Message]
