"""ExpiryMate client"""

from flask import Flask
from flask import current_app

from werkzeug.exceptions import HTTPException

from client import ocr
from client import routes

from client import scans


def refuse(error):
    """Answer HTTP error"""

    if error.code == 413:
        return {"error": "too_big"}, 413

    if error.code == 500:
        return {"error": "failed"}, 500

    return {"error": error.description}, error.code


def crash(error):
    """Record broke scan and answer 500"""

    current_app.logger.exception(error)
    scans.fail(current_app.config["DB"], repr(error))

    return {"error": "failed"}, 500


def create_app(db=None, engine=None):
    """Build Flask"""

    if db is None:
        db = scans.connect()

    if engine is None:
        engine = ocr.load()

    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    app.config["DB"] = db
    app.config["ENGINE"] = engine

    app.register_blueprint(routes.bp)

    app.register_error_handler(HTTPException, refuse)

    app.register_error_handler(Exception, crash)

    return app
