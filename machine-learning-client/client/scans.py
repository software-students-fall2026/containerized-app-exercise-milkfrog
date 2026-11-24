"""Keep records in MongoDB"""

import os

from pymongo import MongoClient


def connect():
    """Open database"""

    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    name = os.environ.get("MONGO_DBNAME", "expirymate")

    return MongoClient(uri, serverSelectionTimeoutMS=3000)[name]
