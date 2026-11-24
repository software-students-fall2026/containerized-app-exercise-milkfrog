"""ExpiryMate client"""

from flask import Flask

from client import routes


def create_app():
    """Build Flask"""

    app = Flask(__name__)

    app.register_blueprint(routes.bp)

    return app
