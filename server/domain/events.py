import dataclasses


@dataclasses.dataclass
class Event:
    def as_dict(self) -> dict:
        data = dataclasses.asdict(self)
        data["__event_name__"] = type(self).__name__
        return data


@dataclasses.dataclass
class ProcessStreamEvent(Event):
    uid: str
    message_template: str
    source_url: str
    source_parser_type: str
    source_encoding: str
    source_tags: list
    receiver_type: str
    receiver_recipient: str
