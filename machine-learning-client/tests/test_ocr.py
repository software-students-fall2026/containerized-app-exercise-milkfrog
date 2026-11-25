"""Tests for ocr"""

import types

import numpy

from client import ocr


def test_read():
    """What engine finds becomes plain lines"""
    box = [[0, 0], [9, 0], [9, 9], [0, 9]]
    result = types.SimpleNamespace(
        txts=("BEST BY",), scores=(numpy.float32(0.5),), boxes=numpy.array([box])
    )
    lines = ocr.read(lambda _image: result, "photo")
    assert lines == [{"text": "BEST BY", "score": 0.5, "box": box}]
    assert isinstance(lines[0]["score"], float)


def test_nothing():
    """photo with no text gives no lines"""
    assert not ocr.read(lambda _image: types.SimpleNamespace(txts=None), "photo")
