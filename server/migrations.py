import mongodex
from pymongo import ASCENDING, TEXT

collections = {
    "sources": [
        mongodex.Index({"slug": ASCENDING}, unique=True),
        mongodex.Index({"name": TEXT}, weights={}),
    ],
    "receivers": [
        mongodex.Index({"slug": ASCENDING}, unique=True),
        mongodex.Index({"name": TEXT}, weights={}),
    ],
    "streams": [
        mongodex.Index({"slug": ASCENDING}, unique=True),
        mongodex.Index({"name": TEXT}, weights={}),
    ],
}


if __name__ == "__main__":
    # TODO from settings
    mongodex.migrate("mongodb://mongo:27017/feed_watchdog", collections)
