"""Tests for dates"""

from client import dates


def read(text):
    """the lines a reader would find in some text"""
    return [{"text": part, "score": 0.95} for part in text.split("\n")]


def test_year_first():
    """A date with the year first"""
    found, problems = dates.find(read("EXP 2026.12.03"))
    assert [item["date"] for item in found] == ["2026-12-03"]
    assert not problems


def test_no_text():
    """No lines at all means no text"""
    found, problems = dates.find([])
    assert not found
    assert problems == ["no_text"]


def test_no_date():
    """Text without a date gives no date"""
    found, problems = dates.find(read("NET WT 12 OZ (340g)"))

    assert not found

    assert problems == ["no_date"]


def test_swap():
    """When month and day can trade places both dates come back, US first"""
    found, problems = dates.find(read("BEST BY 12/03/2026"))
    assert [item["date"] for item in found] == ["2026-12-03", "2026-03-12"]
    assert problems == ["swap"]


def test_two_digit_year():
    """A two digit year means 20xx"""

    found, problems = dates.find(read("SELL BY 11/25/26"))

    assert [item["date"] for item in found] == ["2026-11-25"]

    assert not problems


def test_bad_date():
    """A date that does not exist is not given"""
    found, problems = dates.find(read("EXP 02/30/2026"))

    assert not found

    assert problems == ["bad_date"]


def test_month_name():
    """A full month name"""
    found, problems = dates.find(read("Best if Used By December 3, 2026"))
    assert [item["date"] for item in found] == ["2026-12-03"]
    assert not problems


def test_day_first():
    """A day before the month name"""
    found, problems = dates.find(read("BEST BEFORE 03 DEC 2026"))
    assert [item["date"] for item in found] == ["2026-12-03"]
    assert not problems
