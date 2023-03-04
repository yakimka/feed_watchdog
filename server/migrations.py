import mongodex
from pymongo import ASCENDING, TEXT

from container import container

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
    ],
}


if __name__ == "__main__":
    mongodex.migrate(container.settings().mongo.url, collections)
