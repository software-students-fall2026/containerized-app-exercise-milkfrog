"""Check and open photos"""

import io

from flask import abort

from PIL import Image
from PIL import ImageOps


def check(data):
    """Open photo, or stop request when it cannot be used"""
    if not data:
        abort(400, "empty")

    try:
        image = Image.open(io.BytesIO(data), formats=["JPEG", "PNG"])
        kind = image.format

        image = ImageOps.exif_transpose(image).convert("RGB")

    except OSError:
        abort(400, "not_image")

    width, height = image.size
    return image, {"width": width, "height": height, "size": len(data), "format": kind}
