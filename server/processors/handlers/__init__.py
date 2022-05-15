import importlib
import os
import pkgutil
from functools import lru_cache, partial
from inspect import isclass
from typing import Any, Callable, NamedTuple, Optional

from processors import settings

from . import parsers, receivers

__all__ = [
    "get_registered_handlers",
    "get_parser_by_name",
    "get_receiver_by_name",
    "register_parser",
    "register_receiver",
]


class Handler(NamedTuple):
    name: str
    obj: Callable


HANDLERS: dict[str, list[Handler]] = {
    "parsers": [],
    "receivers": [],
}


# TODO options schema
def register(type: str, name: Optional[str] = None):  # noqa: PLW0622
    def wrapper(func_or_class):
        if isclass(func_or_class):
            handler_name = name or func_or_class.__name__

            handlers_config = settings.HANDLERS_CONFIG
            if subhandlers := handlers_config.get(type, {}).get(handler_name):
                for sub_name, sub_conf in subhandlers.items():
                    kwargs = sub_conf.get("kwargs", {})
                    HANDLERS[type].append(
                        Handler(sub_name, func_or_class(**kwargs))
                    )
            else:
                HANDLERS[type].append(Handler(handler_name, func_or_class()))

        elif callable(func_or_class):
            handler_name = name or func_or_class.__name__
            HANDLERS[type].append(Handler(handler_name, func_or_class))

        return func_or_class

    return wrapper


register_parser = partial(register, "parsers")
register_receiver = partial(register, "receivers")


@lru_cache(maxsize=1)
def get_registered_handlers() -> dict[str, list[Handler]]:
    # Load all parsers and receivers
    _load_modules(parsers)
    _load_modules(receivers)

    # NOTE: global object. Don't modify it
    return HANDLERS


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
