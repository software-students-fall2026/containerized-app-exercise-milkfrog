"""Find dates"""

import calendar
import datetime
import re

NAME = (
    "(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER"
    "|JAN|FEB|MAR|APR|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"
)


def numbers(groups):
    """Turn date into numbers"""
    months = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()

    parts = []

    for part in groups:
        if part.isdigit():
            parts.append(int(part))
        else:
            parts.append(months.index(part[:3].upper()) + 1)
    return parts


def make(year, month, day):
    """a list hold date"""

    if year < 100:
        year = year + 2000

    try:
        return [datetime.date(year, month, day)]
    except ValueError:
        return []


def near(month, day, today):
    """date in next or this or last year closest to today"""

    days = []
    for year in [today.year + 1, today.year, today.year - 1]:
        days = days + make(year, month, day)

    closest = []

    for date in days:
        if not closest or abs(date - today) < abs(closest[0] - today):
            closest = [date]

    return closest


def read(way, parts, today):
    """Turn numbers of date into dates"""

    if way == 1:
        year, month, day = parts
        return make(year, month, day), ""

    if way == 2:
        first, second, year = parts
        days = make(year, first, second)

        if first != second:
            days = days + make(year, second, first)
        note = ""
        if len(days) == 2:
            note = "swap"
        return days, note

    if way == 3:
        month, day, year = parts
        return make(year, month, day), ""

    if way == 4:
        day, month, year = parts
        return make(year, month, day), ""

    if way == 5:
        month, year = parts

        last = calendar.monthrange(year, month)[1]

        return make(year, month, last), "no_day"

    month, day = parts

    return near(month, day, today), "no_year"


def scan(text, today):
    """Find date printed on one line"""
    ways = [
        r"\b(20\d\d)[./-](\d{1,2})[./-](\d{1,2})\b",
        r"\b(\d{1,2})[./-](\d{1,2})[./-](20\d\d|\d\d)\b",
        r"\b" + NAME + r"[ .,/-]*(\d{1,2})[ .,/-]*(20\d\d)\b",
        r"\b(\d{1,2})[ .,/-]*" + NAME + r"[ .,/-]*(20\d\d|\d\d)\b",
        r"\b" + NAME + r"[ .,/-]*(20\d\d)\b",
        r"\b" + NAME + r"[ .,/-]*(\d{1,2})\b",
    ]

    hits = []
    rest = text
    way = 0
    for pattern in ways:
        way = way + 1

        for match in re.finditer(pattern, rest, re.I):
            raw = match.group()
            start = match.start()
            end = match.end()

            days, note = read(way, numbers(match.groups()), today)

            if not days:
                note = "bad_date"

            hits.append({"days": days, "label": "none", "raw": raw, "note": note})

            rest = rest[:start] + "#" * len(raw) + rest[end:]

    return hits


def out(hits):
    """List dates of hits"""

    found = []

    for hit in hits:

        for day in hit["days"]:

            item = {"date": day.isoformat(), "label": hit["label"], "raw": hit["raw"]}

            found.append(item)

    return found


def find(lines, today):
    """Find dates in lines read from photo"""

    if not lines:
        return [], ["no_text"]

    hits = []
    notes = []

    for line in lines:
        text = re.sub(r"\d{1,2}:\d\d", " ", line["text"])

        for hit in scan(text, today):

            if hit["note"]:
                notes.append(hit["note"])

            if hit["days"]:
                hits.append(hit)

    if not hits and "bad_date" not in notes:
        notes.append("no_date")

    problems = []
    for name in "no_text no_date no_year no_day swap bad_date".split():
        if name in notes:
            problems.append(name)

    return out(hits), problems
