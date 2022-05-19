import os
from enum import Enum
from pathlib import Path

import yaml
from decouple import config

BASE_DIR = Path(__file__).parent

REDIS_URL = config("FW_REDIS_PUB_SUB_URL", default="redis://localhost:6379")
SENTRY_DSN = config("FW_SENTRY_DSN", default="")
SHARED_CONFIG_PATH = config(
    "FW_SHARED_CONFIG_PATH", default="/app/handlers.json"
)


class Topic(Enum):
    STREAMS = "streams"


HANDLERS_CONF_PATH = os.environ.get(
    "HANDLERS_CONF_PATH", BASE_DIR / "handlers.yaml"
)
HANDLERS_CONFIG = {}

if HANDLERS_CONF_PATH:

    def string_constructor(self, node):
        value = self.construct_yaml_str(node)
        if value.startswith("ENV:"):
            return os.environ[value[4:]].strip()
        return value

    yaml.Loader.add_constructor(  # type: ignore
        "tag:yaml.org,2002:str", string_constructor
    )
    yaml.SafeLoader.add_constructor(  # type: ignore
        "tag:yaml.org,2002:str", string_constructor
    )

    with open(HANDLERS_CONF_PATH) as conf:
        HANDLERS_CONFIG = yaml.safe_load(conf)
