"""Keep records in MongoDB"""

import datetime

import os

from pymongo import MongoClient


def connect():
    """Open database"""

    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    name = os.environ.get("MONGO_DBNAME", "expirymate")

    return MongoClient(uri, serverSelectionTimeoutMS=3000)[name]


def now():
    """current time"""
    return datetime.datetime.now(datetime.timezone.utc)


def save(db, scan):
    """Store scan and return its id"""

    record = dict(scan)

    record["time"] = now()

    record["status"] = "done"
    result = db.scans.insert_one(record)

    return str(result.inserted_id)
