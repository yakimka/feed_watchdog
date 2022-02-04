from enum import Enum

REDIS_PUB_SUB_URL = "redis://localhost:6379/0"


class Topic(Enum):
    STREAMS = "streams"
