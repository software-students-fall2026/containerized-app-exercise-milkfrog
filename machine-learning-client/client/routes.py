"""Routes for client"""

from flask import Blueprint
from flask import jsonify

bp = Blueprint("routes", __name__)


@bp.get("/health")
def health():
    """Tell caller"""

    return jsonify(status="ok")
