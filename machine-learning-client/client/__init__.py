"""ExpiryMate client"""

from flask import Flask

from werkzeug.exceptions import HTTPException

from client import ocr
from client import routes

from client import scans


def refuse(error):
    """Answer HTTP error"""

    return {"error": error.description}, error.code


def create_app(db=None, engine=None):
    """Build Flask"""

    if db is None:
        db = scans.connect()

    if engine is None:
        engine = ocr.load()

    app = Flask(__name__)

    app.config["DB"] = db
    app.config["ENGINE"] = engine

    app.register_blueprint(routes.bp)

    app.register_error_handler(HTTPException, refuse)

    return app
