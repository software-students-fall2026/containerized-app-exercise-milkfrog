"""Fixtures"""

import io
import types
import mongomock
import numpy
import pytest
from PIL import Image


from client import create_app


def engine(image):
    """Read same two lines from any photo"""
    assert image.mode == "RGB"

    boxes = [[[0, 0], [9, 0], [9, 9], [0, 9]], [[0, 9], [9, 9], [9, 18], [0, 18]]]

    return types.SimpleNamespace(
        txts=("BEST BY", "DEC 03 2026"),
        scores=(numpy.float32(0.98), numpy.float32(0.97)),
        boxes=numpy.array(boxes),
    )


@pytest.fixture(name="db")
def fixture_db():
    """Give empty fake database"""

    return mongomock.MongoClient().expirymate


@pytest.fixture(name="app")
def fixture_app(db):
    """Build app around fake database and fake engine"""

    return create_app(db, engine)


@pytest.fixture(name="client")
def fixture_client(app):
    """Give a test client"""
    return app.test_client()


@pytest.fixture(name="jpeg")
def fixture_jpeg():
    """Give bytes of JPEG photo"""
    data = io.BytesIO()

    Image.new("RGB", (60, 40), "white").save(data, "JPEG")

    return data.getvalue()
