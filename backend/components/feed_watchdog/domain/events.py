import dataclasses
from typing import Any

from dacite import from_dict

from feed_watchdog.domain.models import Post


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
    squash: bool
    message_template: str
    modifiers: list[ModifierData]
    source: SourceData
    receiver: ReceiverData


@dataclasses.dataclass
class PostParsed(Event):
    stream_slug: str
    post: Post
