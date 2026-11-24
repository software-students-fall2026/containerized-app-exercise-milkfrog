"""Test routes"""

import io

from client import create_app, ocr, scans


def post(client, data):
    """Send bytes to scan route as photo"""
    return client.post("/scan", data={"photo": (io.BytesIO(data), "photo.jpg")})


def test_defaults(monkeypatch):
    """Without arguments app opens database and starts engine"""
    monkeypatch.setattr(scans, "connect", lambda: "db")
    monkeypatch.setattr(ocr, "load", lambda: "engine")
    app = create_app()
    assert app.config["DB"] == "db"
    assert app.config["ENGINE"] == "engine"


def test_health(client):
    """health route answers ok"""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.get_json() == {"status": "ok"}


def test_scan(client, db, jpeg):
    """photo gives its text and dates, and scan is stored"""
    reply = post(client, jpeg)
    record = db.scans.find_one()
    assert reply.status_code == 200
    assert reply.get_json() == {
        "id": str(record["_id"]),
        "text": "BEST BY\nDEC 03 2026",
        "dates": [{"date": "2026-12-03", "label": "best", "raw": "DEC 03 2026"}],
        "problems": [],
    }
    assert set(record) == {
        "_id",
        "time",
        "status",
        "text",
        "dates",
        "problems",
        "lines",
        "engine",
        "ms",
        "photo",
    }
    assert record["status"] == "done"
    assert record["engine"] == "rapidocr"


def test_no_photo(client):
    """request without photo is refused"""
    reply = client.post("/scan", data={})
    assert reply.status_code == 400
    assert reply.get_json() == {"error": "no_photo"}


def test_empty(client):
    """empty photo is refused"""
    reply = post(client, b"")
    assert reply.status_code == 400
    assert reply.get_json() == {"error": "empty"}


def test_not_image(client):
    """file that is not JPEG or PNG is refused"""
    reply = post(client, b"this is not a photo")
    assert reply.status_code == 400
    assert reply.get_json() == {"error": "not_image"}
