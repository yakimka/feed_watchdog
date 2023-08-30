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
    ],
}


def migrate(mongo_url: str):
    mongodex.migrate(mongo_url, collections)
