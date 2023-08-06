from __future__ import annotations

from typing import TYPE_CHECKING

from feed_watchdog.repositories.processor import FileProcessorsConfigRepo

if TYPE_CHECKING:
    from feed_watchdog.domain.interfaces import (
        IProcessorsConfigurationRepository,
    )


def get_processors_conf_repo() -> IProcessorsConfigurationRepository:
    return FileProcessorsConfigRepo("/app/handlers.json")
