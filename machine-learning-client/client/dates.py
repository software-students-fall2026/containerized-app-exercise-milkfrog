"""Find dates"""

import datetime
import re


def make(year, month, day):
    """a list hold date"""

    return [datetime.date(year, month, day)]


def scan(text):
    """Find date printed on one line"""

    hits = []

    for match in re.finditer(r"\b(20\d\d)[./-](\d{1,2})[./-](\d{1,2})\b", text):
        year, month, day = match.groups()
        days = make(int(year), int(month), int(day))

        hits.append({"days": days, "label": "none", "raw": match.group()})

    return hits


def out(hits):
    """List dates of hits"""

    found = []

    for hit in hits:

        for day in hit["days"]:

            item = {"date": day.isoformat(), "label": hit["label"], "raw": hit["raw"]}

            found.append(item)

    return found


def find(lines):
    """Find dates in lines read from photo"""

    if not lines:
        return [], ["no_text"]

    hits = []

    for line in lines:
        hits = hits + scan(line["text"])

    problems = []

    if not hits:
        problems.append("no_date")

    return out(hits), problems
