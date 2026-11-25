"""Tests for dates"""

import datetime

from client import dates

TODAY = datetime.date(2026, 11, 20)


def read(text):
    """the lines a reader would find in some text"""
    return [{"text": part, "score": 0.95} for part in text.split("\n")]


def test_year_first():
    """A date with the year first"""
    found, problems = dates.find(read("EXP 2026.12.03"), TODAY)
    assert [item["date"] for item in found] == ["2026-12-03"]
    assert not problems


def test_no_text():
    """No lines at all means no text"""
    found, problems = dates.find([], TODAY)
    assert not found
    assert problems == ["no_text"]


def test_no_date():
    """Text without a date gives no date"""
    found, problems = dates.find(read("NET WT 12 OZ (340g)"), TODAY)

    assert not found

    assert problems == ["no_date"]


def test_read_once():
    """Text already read as a date is not read again"""
    found, problems = dates.find(read("JUN 2026.12.03 7"), TODAY)
    assert found == [{"date": "2026-12-03", "label": "none", "raw": "2026.12.03"}]
    assert not problems


def test_swap():
    """When month and day can trade places both dates come back, US first"""
    found, problems = dates.find(read("BEST BY 12/03/2026"), TODAY)
    assert [item["date"] for item in found] == ["2026-12-03", "2026-03-12"]
    assert problems == ["swap"]


def test_two_digit_year():
    """A two digit year means 20xx"""

    found, problems = dates.find(read("SELL BY 11/25/26"), TODAY)

    assert [item["date"] for item in found] == ["2026-11-25"]

    assert not problems


def test_bad_date():
    """A date that does not exist is not given"""
    found, problems = dates.find(read("EXP 02/30/2026"), TODAY)

    assert not found

    assert problems == ["bad_date"]


def test_month_name():
    """A full month name"""
    found, problems = dates.find(read("Best if Used By December 3, 2026"), TODAY)
    assert [item["date"] for item in found] == ["2026-12-03"]
    assert not problems


def test_day_first():
    """A day before the month name"""
    found, problems = dates.find(read("BEST BEFORE 03 DEC 2026"), TODAY)
    assert [item["date"] for item in found] == ["2026-12-03"]
    assert not problems


def test_no_day():
    """A month and a year give the last day of the month"""
    found, problems = dates.find(read("EXP FEB 2028"), TODAY)
    assert [item["date"] for item in found] == ["2028-02-29"]
    assert problems == ["no_day"]


def test_no_year():
    """A month and a day get the year closest to today"""
    found, problems = dates.find(read("BEST BY JAN 15"), TODAY)
    assert [item["date"] for item in found] == ["2027-01-15"]
    assert problems == ["no_year"]
    found, _ = dates.find(read("BEST BY DEC 28"), datetime.date(2027, 1, 5))
    assert [item["date"] for item in found] == ["2026-12-28"]


def test_time():
    """A time is not read as part of a date"""
    found, problems = dates.find(read("BEST BY 9:26 MAR 2027"), TODAY)
    assert [item["date"] for item in found] == ["2027-03-31"]
    assert problems == ["no_day"]
