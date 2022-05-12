from enum import Enum

from decouple import config

REDIS_PUB_SUB_URL = config(
    "FW_REDIS_PUB_SUB_URL", default="redis://localhost:6379"
)


class Topic(Enum):
    STREAMS = "streams"
