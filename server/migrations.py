import mongodex
from pymongo import ASCENDING

collections = {
    "sources": [
        mongodex.Index({"slug": ASCENDING}, unique=True),
    ],
}


if __name__ == "__main__":
    # TODO from settings
    mongodex.migrate("mongodb://mongo:27017/feed_watchdog", collections)
