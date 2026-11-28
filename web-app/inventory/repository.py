"""Shared food storage and validation for inventory, scans and reminders."""

import re
from datetime import date

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

LABELS = {
    "best": "Best by",
    "use": "Use by",
    "sell": "Sell by",
    "exp": "Expires",
    "none": "Unspecified",
}
PLACES = {"fridge": "Fridge", "freezer": "Freezer", "pantry": "Pantry"}
STATUSES = {"active", "consumed", "discarded"}


def object_id(value):
    """Return a database key, or None when the input is not a valid ID."""
    return ObjectId(value) if ObjectId.is_valid(value) else None


def parse_date(value):
    """Read an exact YYYY-MM-DD calendar date."""
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        raise ValueError("Enter a valid package date in YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Enter a valid package date in YYYY-MM-DD format.") from error


def _validated(fields, *, partial=False):
    values = {}
    for field in ("name", "date", "label", "place"):
        if partial and field not in fields:
            continue
        value = fields.get(field)
        if field == "name":
            if not isinstance(value, str) or not 1 <= len(value.strip()) <= 100:
                raise ValueError("Enter a food name of 1–100 characters.")
            value = value.strip()
        elif field == "date":
            value = parse_date(value).isoformat()
        elif field == "label" and (not isinstance(value, str) or value not in LABELS):
            raise ValueError("Choose a valid date label.")
        elif field == "place" and (not isinstance(value, str) or value not in PLACES):
            raise ValueError("Choose a valid storage location.")
        values[field] = value
    return values


def _public(document):
    return {
        "id": str(document["_id"]),
        **{key: value for key, value in document.items() if key != "_id"},
    }


def add(db, food, *, request_id=None):
    """Create active food and return its string ID. Repeated request IDs save once."""
    document = _validated(food)
    if food.get("scan") is not None:
        scan_key = object_id(food["scan"])
        if scan_key is None:
            raise ValueError("Invalid linked scan.")
        document["scan"] = str(scan_key)
    document["status"] = "active"
    if request_id is None:
        return str(db.foods.insert_one(document).inserted_id)
    key = object_id(request_id)
    if key is None:
        raise ValueError("Invalid submission. Reload the form and try again.")
    try:
        db.foods.update_one({"_id": key}, {"$setOnInsert": document}, upsert=True)
    except DuplicateKeyError:
        # A concurrent upsert can win the race to insert the same key.
        if not db.foods.find_one({"_id": key}):
            raise
    return str(key)


def get(db, key):
    """Return a food by ID, or None."""
    key = object_id(key)
    document = db.foods.find_one({"_id": key}) if key is not None else None
    return _public(document) if document is not None else None


def find(db, status="active", place=None, word=None, *, descending=False):
    """Find foods in date order with optional place and literal name filters."""
    if status not in STATUSES:
        raise ValueError("Invalid food status.")
    query = {"status": status}
    if place:
        if place not in PLACES:
            raise ValueError("Invalid storage location.")
        query["place"] = place
    if word and (word := word.strip()):
        query["name"] = {"$regex": re.escape(word), "$options": "i"}
    direction = -1 if descending else 1
    return [
        _public(item)
        for item in db.foods.find(query).sort([("date", direction), ("_id", 1)])
    ]


def edit(db, key, changes):
    """Update editable fields and return whether the food exists."""
    values = _validated(changes, partial=True)
    if not values:
        return get(db, key) is not None
    return _update(db, key, values)


def mark(db, key, status):
    """Update food status for D's history and reminder routes."""
    if status not in STATUSES:
        raise ValueError("Invalid food status.")
    return _update(db, key, {"status": status})


def _update(db, key, values):
    key = object_id(key)
    if key is None:
        return False
    return bool(db.foods.update_one({"_id": key}, {"$set": values}).matched_count)
