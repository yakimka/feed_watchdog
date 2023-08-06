from __future__ import annotations

import dataclasses
import importlib
import os
import pkgutil
from collections import defaultdict
from enum import Enum
from functools import partial
from inspect import isclass
from pathlib import Path
from typing import Any, Callable, NamedTuple, Optional, Type, TypedDict

import yaml

__all__ = [
    "get_registered_handlers",
    "get_handler_by_name",
    "register_handler",
    "HandlerOptions",
    "HandlerType",
    "init_handlers_config",
    "get_handler_return_model_by_name",
]

from feed_watchdog.domain.models import Post


class HandlerType(Enum):
    fetchers = "fetchers"
    parsers = "parsers"
    receivers = "receivers"
    modifiers = "modifiers"


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
            field_type = field.type
            extra_properties = {}
            is_enum = isclass(field.type) and issubclass(field.type, Enum)
            if is_enum:
                field_type = _get_enum_values_type(field.type)
                extra_properties["enum"] = [field.value for field in field.type]
            schema["properties"][field.name] = {
                **extra_properties,
                "type": _python_type_to_json_schema_type(field_type),
                "title": cls.field_title(field.name),
                "description": cls.field_description(field.name),
            }

            if field.default is not m:
                default = field.default.value if is_enum else field.default
                schema["properties"][field.name]["default"] = default
            elif field.default_factory is not m:
                schema["properties"][field.name][
                    "default"
                ] = field.default_factory()
            else:
                schema["required"].append(field.name)

        return schema


ReturnModel = Type[Post]


class Handler(NamedTuple):
    name: str
    obj: Callable
    options_class: Optional[Type[HandlerOptions]]
    return_fields_schema: Optional[dict]
    return_model: Optional[ReturnModel]


RawHandler = tuple[
    str,
    Callable,
    Optional[dict],
    Optional[Type[HandlerOptions]],
    Optional[dict],
    Optional[ReturnModel],
]
HANDLERS: dict[str, dict[str, RawHandler]] = defaultdict(dict)
HANDLERS_CONFIG: dict = {}


def init_handlers_config(
    path_to_config: Path | str, env_prefix: str = "FW_HNDR_"
):
    global HANDLERS_CONFIG
    if not HANDLERS_CONFIG:
        string_constructor = partial(
            _yaml_string_constructor, env_prefix=env_prefix
        )
        yaml.Loader.add_constructor("tag:yaml.org,2002:str", string_constructor)
        yaml.SafeLoader.add_constructor(
            "tag:yaml.org,2002:str", string_constructor
        )

        with open(path_to_config) as conf:
            HANDLERS_CONFIG = yaml.safe_load(conf)


def _yaml_string_constructor(self, node, env_prefix):
    value = self.construct_yaml_str(node)
    if value.startswith("ENV:"):
        return os.environ[f"{env_prefix}{value[4:]}"].strip()
    return value


def register_handler(
    type: str,  # noqa: PLW0622
    name: Optional[str] = None,
    options: Optional[Type[HandlerOptions]] = None,
    return_fields_schema: Optional[dict] = None,
    return_model: Optional[ReturnModel] = None,
):  # noqa: PLW0622
    def wrapper(func_or_class):
        if type == HandlerType.parsers.value:
            if not return_model:
                raise ValueError("Parsers must be registered with return_model")

        if isclass(func_or_class):
            handler_name = name or func_or_class.__name__

            if subhandlers := HANDLERS_CONFIG.get(type, {}).get(handler_name):
                for sub_name, sub_conf in subhandlers.items():
                    kwargs = sub_conf.get("kwargs", {})
                    HANDLERS[type][sub_name] = (
                        sub_name,
                        func_or_class,
                        kwargs,
                        options,
                        return_fields_schema,
                        return_model,
                    )
            else:
                HANDLERS[type][handler_name] = (
                    handler_name,
                    func_or_class,
                    {},
                    options,
                    return_fields_schema,
                    return_model,
                )

        elif callable(func_or_class):
            handler_name = name or func_or_class.__name__
            HANDLERS[type][handler_name] = (
                handler_name,
                func_or_class,
                None,
                options,
                return_fields_schema,
                return_model,
            )

        return func_or_class

    return wrapper


def load_handlers() -> None:
    for item in HandlerType:
        package = importlib.import_module(
            f".{item.value}", package="feed_watchdog.handlers"
        )
        _load_modules(package)


def get_registered_handlers() -> dict[str, dict[str, Handler]]:
    load_handlers()

    result = {}
    for handler_type, handlers in HANDLERS.items():
        result[handler_type] = {
            name: Handler(
                name_,
                obj if kwargs is None else obj(**kwargs),
                options_class,
                return_fields_schema,
                return_model,
            )
            for name, (
                name_,
                obj,
                kwargs,
                options_class,
                return_fields_schema,
                return_model,
            ) in handlers.items()
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


def get_handler_return_model_by_name(type: str, name: str) -> ReturnModel:
    registered_handlers = get_registered_handlers()
    handler = dict(registered_handlers[type])[name]
    if handler.return_model is None:
        raise ValueError(f"Handler {name} does not have return model")
    return handler.return_model


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


def _python_type_to_json_schema_type(python_type: Type | str) -> str:
    types = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
    }
    python_type = (
        python_type if isinstance(python_type, str) else python_type.__name__
    )
    try:
        return types[python_type]
    except KeyError:
        raise ValueError(f"Unsupported type {python_type}") from None


def _get_enum_values_type(enum_class: Type[Enum]) -> Type:
    enums: list[Enum] = list(enum_class)
    klass = type(enums[0].value)
    is_consistent = all(isinstance(e.value, klass) for e in enums)
    if not is_consistent:
        raise ValueError(
            f"Enum {enum_class.__name__} has inconsistent values types"
        )

    return klass
