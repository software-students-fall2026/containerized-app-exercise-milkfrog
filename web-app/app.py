"""Flask entry point for the ExpiryMate web subsystem."""

import os
from secrets import compare_digest, token_hex

from flask import Flask, abort, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from inventory.routes import inventory
from scans.routes import scans
from scans.service import MAX_REQUEST_BYTES


def create_app(config=None):
    """Create the application, with an optional database override for tests."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY") or token_hex(32),
        MONGO_URI=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        MONGO_DBNAME=os.getenv("MONGO_DBNAME", "expirymate"),
        ML_URL=os.getenv("ML_URL", "http://ml:8000"),
        MOCK_OCR=os.getenv("MOCK_OCR") == "1",
        MAX_CONTENT_LENGTH=MAX_REQUEST_BYTES,
        SESSION_COOKIE_SAMESITE="Lax",
        INVENTORY_REMINDER=None,
    )
    if config:
        app.config.update(config)

    db = app.config.get("DATABASE")
    if db is None:
        mongo = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=3000)
        db = mongo[app.config["MONGO_DBNAME"]]
    app.extensions["expirymate_db"] = db

    app.register_blueprint(inventory)
    app.register_blueprint(scans)
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def protect_forms():
        if request.method == "POST":
            expected = session.get("csrf_token", "")
            submitted = request.form.get("csrf_token", "")
            if not expected or not compare_digest(
                expected.encode(), submitted.encode()
            ):
                abort(400, "Reload the form and try again.")

    @app.get("/")
    def home():
        return redirect(url_for("inventory.index"))

    @app.errorhandler(400)
    @app.errorhandler(404)
    def bad_request(error):
        return (
            render_template("error.html", title=error.name, message=error.description),
            error.code,
        )

    @app.errorhandler(413)
    def too_large(_error):
        return (
            render_template(
                "error.html",
                title="Photo is too large",
                message="Choose a JPEG or PNG under 10 MB and try again.",
            ),
            413,
        )

    @app.errorhandler(PyMongoError)
    def database_unavailable(error):
        app.logger.error("MongoDB operation failed: %s", type(error).__name__)
        return (
            render_template(
                "error.html",
                title="Database unavailable",
                message="Your request could not be completed. Please try again shortly.",
            ),
            503,
        )

    return app


def csrf_token():
    """Return a token tied to this browser session."""
    if "csrf_token" not in session:
        session["csrf_token"] = token_hex(32)
    return session["csrf_token"]
