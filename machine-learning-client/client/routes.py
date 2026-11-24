"""Routes for client"""

import datetime
import time

from flask import Blueprint
from flask import current_app


from flask import jsonify
from flask import request

from client import dates
from client import ocr

from client import photos
from client import scans

bp = Blueprint("routes", __name__)


@bp.get("/health")
def health():
    """Tell caller"""

    return jsonify(status="ok")


@bp.post("/scan")
def scan():
    """Read dates"""
    upload = request.files.get("photo")

    image, photo = photos.check(upload.read())
    start = time.perf_counter()
    lines = ocr.read(current_app.config["ENGINE"], image)
    took = round((time.perf_counter() - start) * 1000)

    found, problems = dates.find(lines, datetime.date.today())

    text = "\n".join(line["text"] for line in lines)

    record = {
        "text": text,
        "dates": found,
        "problems": problems,
        "lines": lines,
        "engine": ocr.NAME,
        "ms": took,
        "photo": photo,
    }
    key = scans.save(current_app.config["DB"], record)

    return jsonify(id=key, text=text, dates=found, problems=problems)
