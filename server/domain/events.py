import dataclasses


@dataclasses.dataclass
class Event:
    def as_dict(self) -> dict:
        data = dataclasses.asdict(self)
        data["__event_name__"] = type(self).__name__
        return data


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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            slug=data["slug"],
            squash=data["squash"],
            message_template=data["message_template"],
            modifiers=data["modifiers"],
            source=SourceData(
                fetcher_type=data["source"]["fetcher_type"],
                fetcher_options=data["source"]["fetcher_options"],
                parser_type=data["source"]["parser_type"],
                parser_options=data["source"]["parser_options"],
                tags=data["source"]["tags"],
            ),
            receiver=ReceiverData(
                type=data["receiver"]["type"],
                options=data["receiver"]["options"],
            ),
        )
