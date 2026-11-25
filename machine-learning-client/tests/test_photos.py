"""Tests for photos"""

import io

from PIL import ExifTags, Image

from client import photos


def test_turned():
    """grey photo taken sideways is turned upright and made RGB"""
    exif = Image.Exif()
    exif[ExifTags.Base.Orientation] = 6
    buffer = io.BytesIO()
    Image.new("L", (60, 40), 200).save(buffer, "PNG", exif=exif)
    data = buffer.getvalue()
    image, photo = photos.check(data)
    assert image.mode == "RGB"
    assert image.size == (40, 60)
    assert photo == {"width": 40, "height": 60, "size": len(data), "format": "PNG"}
