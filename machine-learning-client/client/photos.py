"""Check and open photos"""

import io

from PIL import Image


def check(data):
    """Open photo"""

    image = Image.open(io.BytesIO(data), formats=["JPEG", "PNG"])
    kind = image.format

    width, height = image.size
    return image, {"width": width, "height": height, "size": len(data), "format": kind}
