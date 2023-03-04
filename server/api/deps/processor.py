from __future__ import annotations

from typing import TYPE_CHECKING

from adapters.repositories.processor import FileProcessorsConfigRepo

if TYPE_CHECKING:
    from domain.interfaces import IProcessorsConfigurationRepository


def get_processors_conf_repo() -> IProcessorsConfigurationRepository:
    return FileProcessorsConfigRepo("/app/handlers.json")
