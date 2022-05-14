from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sentry_sdk import capture_message

if TYPE_CHECKING:
    from logging import Logger


def write_warn_message(message: str, logger: Optional[Logger] = None) -> None:
    capture_message(message, level="warning")
    if logger:
        logger.warning(message)
