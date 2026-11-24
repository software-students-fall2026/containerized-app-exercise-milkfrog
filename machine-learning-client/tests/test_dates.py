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
