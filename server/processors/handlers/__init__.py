from __future__ import annotations

import dataclasses
import importlib
import os
import pkgutil
from collections import defaultdict
from enum import Enum
from functools import partial
from inspect import isclass
from typing import Any, Callable, NamedTuple, Optional, Type, TypedDict

__all__ = [
    "get_registered_handlers",
    "get_handler_by_name",
    "register_handler",
    "HandlerOptions",
    "HandlerType",
]


class HandlerType(Enum):
    fetchers = "fetchers"
    parsers = "parsers"
    receivers = "receivers"


@dataclasses.dataclass
class HandlerOptions:
    DESCRIPTIONS = {}  # type: dict[str, tuple[str, str]]

    @classmethod
    def _descriptions(cls) -> dict[str, tuple[str, str]]:
        return {
            field.name: cls.DESCRIPTIONS[field.name]
            for field in dataclasses.fields(cls)
            if field.name in cls.DESCRIPTIONS
        }

    @classmethod
    def field_title(cls, field_name: str) -> str:
        title = 0
        return cls._descriptions().get(field_name, ("", ""))[title]

    @classmethod
    def field_description(cls, field_name: str) -> str:
        description = 1
        return cls._descriptions().get(field_name, ("", ""))[description]

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
            type_name = field.type
            if not isinstance(type_name, str):
                type_name = type_name.__name__
            schema["properties"][field.name] = {
                "type": _python_type_to_json_schema_type(type_name),
                "title": cls.field_title(field.name),
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


class Handler(NamedTuple):
    name: str
    obj: Callable
    options_class: Optional[Type[HandlerOptions]]


RawHandler = tuple[
    str, Callable, Optional[dict], Optional[Type[HandlerOptions]]
]
HANDLERS: dict[str, dict[str, RawHandler]] = defaultdict(dict)


def register_handler(
    type: str,  # noqa: PLW0622
    name: Optional[str] = None,
    options: Optional[Type[HandlerOptions]] = None,
):  # noqa: PLW0622
    def wrapper(func_or_class):
        from processors import settings  # noqa: PLC0415

        if isclass(func_or_class):
            handler_name = name or func_or_class.__name__

            handlers_config = settings.HANDLERS_CONFIG
            if subhandlers := handlers_config.get(type, {}).get(handler_name):
                for sub_name, sub_conf in subhandlers.items():
                    kwargs = sub_conf.get("kwargs", {})
                    HANDLERS[type][sub_name] = (
                        sub_name,
                        func_or_class,
                        kwargs,
                        options,
                    )
            else:
                HANDLERS[type][handler_name] = (
                    handler_name,
                    func_or_class,
                    {},
                    options,
                )

        elif callable(func_or_class):
            handler_name = name or func_or_class.__name__
            HANDLERS[type][handler_name] = (
                handler_name,
                func_or_class,
                None,
                options,
            )

        return func_or_class

    return wrapper


def load_handlers() -> None:
    for item in HandlerType:
        package = importlib.import_module(
            f".{item.value}", package="processors.handlers"
        )
        _load_modules(package)


def get_registered_handlers() -> dict[str, dict[str, Handler]]:
    load_handlers()

    result = {}
    for handler_type, handlers in HANDLERS.items():
        result[handler_type] = {
            name: Handler(
                name_, obj if kwargs is None else obj(**kwargs), options_class
            )
            for name, (name_, obj, kwargs, options_class) in handlers.items()
        }
    return result


def _load_modules(package) -> None:
    for module_name in _parse_modules(package):
        importlib.import_module(f".{module_name}", package=package.__name__)


def _parse_modules(package) -> list[str]:
    pkgpath = os.path.dirname(package.__file__)
    return [name for _, name, _ in pkgutil.iter_modules([pkgpath])]


def get_handler_by_name(
    type: str, name: str, options: Optional[dict] = None  # noqa: PLW0622
) -> Any:
    registered_handlers = get_registered_handlers()
    handler = dict(registered_handlers[type])[name]
    options_ = None
    if options and handler.options_class:
        options_ = handler.options_class(**options)
    return partial(handler.obj, options=options_)


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
