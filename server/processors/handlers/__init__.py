import dataclasses
import importlib
import os
import pkgutil
from collections import defaultdict
from functools import lru_cache, partial
from inspect import isclass
from typing import Any, Callable, NamedTuple, Optional, TypedDict

from processors import settings

from . import parsers, receivers

__all__ = [
    "get_registered_handlers",
    "get_parser_by_name",
    "get_receiver_by_name",
    "register_parser",
    "register_receiver",
    "HandlerOptions",
]


class Handler(NamedTuple):
    name: str
    obj: Callable
    options: Optional[dict]


HANDLERS: dict[str, dict[str, Handler]] = defaultdict(dict)


def register_handler(
    type: str,  # noqa: PLW0622
    name: Optional[str] = None,
    options: Optional[dict] = None,
):  # noqa: PLW0622
    def wrapper(func_or_class):
        if isclass(func_or_class):
            handler_name = name or func_or_class.__name__

            handlers_config = settings.HANDLERS_CONFIG
            if subhandlers := handlers_config.get(type, {}).get(handler_name):
                for sub_name, sub_conf in subhandlers.items():
                    kwargs = sub_conf.get("kwargs", {})
                    HANDLERS[type][sub_name] = Handler(
                        sub_name, func_or_class(**kwargs), options
                    )
            else:
                HANDLERS[type][handler_name] = Handler(
                    handler_name, func_or_class(), options
                )

        elif callable(func_or_class):
            handler_name = name or func_or_class.__name__
            HANDLERS[type][handler_name] = Handler(
                handler_name, func_or_class, options
            )

        return func_or_class

    return wrapper


register_parser = partial(register_handler, "parsers")
register_receiver = partial(register_handler, "receivers")


@lru_cache(maxsize=1)
def get_registered_handlers() -> dict[str, dict[str, Handler]]:
    # Load all parsers and receivers
    _load_modules(parsers)
    _load_modules(receivers)

    # NOTE: global object. Don't modify it
    return dict(HANDLERS)


def _load_modules(package) -> None:
    for module_name in _parse_modules(package):
        importlib.import_module(f".{module_name}", package=package.__name__)


def _parse_modules(package) -> list[str]:
    pkgpath = os.path.dirname(package.__file__)
    return [name for _, name, _ in pkgutil.iter_modules([pkgpath])]


def get_parser_by_name(name: str) -> Any:
    registered_handlers = get_registered_handlers()
    return dict(registered_handlers["parsers"])[name]


def get_receiver_by_name(name: str) -> Any:
    registered_handlers = get_registered_handlers()
    return dict(registered_handlers["receivers"])[name]


Schema = TypedDict(
    "Schema",
    {
        "$schema": str,
        "title": str,
        "type": str,
        "properties": dict,
        "required": list,
    },
)


@dataclasses.dataclass
class HandlerOptions:
    DESCRIPTIONS = {}  # type: dict[str, str]

    @classmethod
    def descriptions(cls) -> dict[str, str]:
        return {
            field.name: cls.DESCRIPTIONS[field.name]
            for field in dataclasses.fields(cls)
            if field.name in cls.DESCRIPTIONS
        }

    @classmethod
    def field_description(cls, field_name: str) -> str:
        return cls.descriptions().get(field_name, "")

    @classmethod
    def to_json_schema(cls) -> Schema:
        schema: Schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": type(cls).__name__,
            "type": "object",
            "properties": {},
            "required": [],
        }
        for field in dataclasses.fields(cls):
            m = dataclasses.MISSING
            schema["properties"][field.name] = {
                "type": _python_type_to_json_schema_type(str(field.type)),
                "description": cls.field_description(field.name),
            }
            if field.default is not m:
                schema["properties"][field.name]["default"] = field.default
            elif field.default_factory is not m:  # type: ignore
                schema["properties"][field.name][
                    "default"
                ] = field.default_factory()
            else:
                schema["required"].append(field.name)

        return schema


def _python_type_to_json_schema_type(python_type: str) -> str:
    types = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
    }
    try:
        return types[python_type]
    except KeyError:
        raise ValueError(f"Unsupported type {python_type}") from None
