"""Tests for scans"""

import mongomock

from client import scans


def test_connect(monkeypatch):
    """database address and name come from environment"""
    monkeypatch.setenv("MONGO_URI", "mongodb://db:27017")
    monkeypatch.setenv("MONGO_DBNAME", "pantry")
    monkeypatch.setattr(scans, "MongoClient", mongomock.MongoClient)
    db = scans.connect()
    assert db.name == "pantry"
    assert db.client.address == ("db", 27017)
