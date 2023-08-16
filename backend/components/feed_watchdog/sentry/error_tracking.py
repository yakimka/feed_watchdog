from logging import Logger
from typing import Optional

from sentry_sdk import capture_message


def write_warn_message(message: str, logger: Optional[Logger] = None) -> None:
    if logger:
        logger.warning(message)
    capture_message(message, level="warning")
