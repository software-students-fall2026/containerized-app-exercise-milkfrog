"""RapidOCR"""

from rapidocr import RapidOCR

NAME = "rapidocr"


def load():
    """Start engine"""
    return RapidOCR()


def read(engine, image):
    """Read text"""

    result = engine(image)

    if result.txts is None:
        return []

    lines = []
    for text, score, box in zip(result.txts, result.scores, result.boxes):
        lines.append({"text": text, "score": float(score), "box": box.tolist()})

    return lines
