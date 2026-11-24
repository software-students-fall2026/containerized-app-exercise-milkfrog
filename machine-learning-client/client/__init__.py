"""ExpiryMate client"""

from flask import Flask

from client import ocr
from client import routes

from client import scans


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

    return app
