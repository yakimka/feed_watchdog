import importlib
import os
import pkgutil
from typing import Any

from processors import settings


def _parse_modules(package: str) -> list[str]:
    pkgpath = os.path.dirname(package)
    return [name for _, name, _ in pkgutil.iter_modules([pkgpath])]


def get_registered_handlers() -> dict[str, list[Any]]:
    from . import parsers, receivers  # noqa: PLC0415

    handlers: dict[str, list[Any]] = {
        "parsers": [],
        "receivers": [],
    }
    for module_name in _parse_modules(parsers.__file__):
        mod = importlib.import_module(
            f".{module_name}", package="handlers.parsers"
        )
        handlers["parsers"].append((module_name, mod.handler))

    handlers_config = settings.HANDLERS_CONFIG
    for module_name in _parse_modules(receivers.__file__):
        mod = importlib.import_module(
            f".{module_name}", package="handlers.receivers"
        )
        if subhandlers := handlers_config.get("receivers", {}).get(module_name):
            for sub_name, sub_conf in subhandlers.items():
                kwargs = sub_conf.get("kwargs", {})
                handlers["receivers"].append((sub_name, mod.Sender(**kwargs)))
        else:
            handlers["receivers"].append((module_name, mod.Sender()))
    return handlers


def get_parser_by_name(name: str) -> Any:
    registered_handlers = get_registered_handlers()
    return dict(registered_handlers["parsers"])[name]


def get_receiver_by_name(name: str) -> Any:
    registered_handlers = get_registered_handlers()
    return dict(registered_handlers["receivers"])[name]


__all__ = [
    "get_registered_handlers",
    "get_parser_by_name",
    "get_receiver_by_name",
]
