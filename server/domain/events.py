import dataclasses

from domain.models import Modifier


@dataclasses.dataclass
class Event:
    def as_dict(self) -> dict:
        data = dataclasses.asdict(self)
        data["__event_name__"] = type(self).__name__
        return data


@dataclasses.dataclass
class ProcessStreamEvent(Event):
    uid: str
    squash: bool
    message_template: str
    source_fetcher_type: str
    source_fetcher_options: dict
    source_parser_type: str
    source_parser_options: dict
    source_tags: list
    receiver_type: str
    receiver_options: dict
    modifiers: list[Modifier]
