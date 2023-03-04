import json
from pathlib import Path

from domain.interfaces import IProcessorsConfigurationRepository


class FileProcessorsConfigRepo(IProcessorsConfigurationRepository):
    def __init__(self, path: str | Path):
        self._key = "handlers"
        self._config_path = Path(path)

    def get_config(self, handler: str) -> dict:
        config = self._load_configuration()
        return {
            item["type"]: item["options"] for item in config.get(handler, [])
        }

    def _load_configuration(self) -> dict:
        with open(self._config_path) as fp:
            return json.load(fp).get(self._key, {})
