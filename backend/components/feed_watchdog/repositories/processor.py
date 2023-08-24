from pathlib import Path

from feed_watchdog.domain.interfaces import IProcessorsConfigurationRepository
from feed_watchdog.handlers import init_handlers_config
from feed_watchdog.handlers.configuration import parse_configuration


class FileProcessorsConfigRepo(IProcessorsConfigurationRepository):
    def __init__(self, handlers_conf_path: str | Path):
        self._key = "handlers"
        self._handlers_conf_path = Path(handlers_conf_path)

    def get_config(self, handler: str) -> dict:
        config = self._get_configuration()
        return {item["type"]: item["options"] for item in config.get(handler, [])}

    def _get_configuration(self) -> dict:
        init_handlers_config(self._handlers_conf_path)
        return parse_configuration().get(self._key, {})
