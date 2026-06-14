"""Working-day date calculator — Mon–Fri, no public holidays (per UC3 spec)."""

from datetime import date, timedelta


def is_working_day(d: date) -> bool:
    """Mon=0 … Fri=4 are working days; Sat=5 / Sun=6 are not."""
    return d.weekday() < 5


def add_working_days(start: date, n: int) -> date:
    """Return the date that is exactly n working days after start."""
    d = start
    count = 0
    while count < n:
        d += timedelta(days=1)
        if is_working_day(d):
            count += 1
    return d


def subtract_working_days(start: date, n: int) -> date:
    """Return the date that is exactly n working days before start."""
    d = start
    count = 0
    while count < n:
        d -= timedelta(days=1)
        if is_working_day(d):
            count += 1
    return d


def add_calendar_days(start: date, n: int) -> date:
    """Add n calendar days (Sat/Sun count)."""
    return start + timedelta(days=n)


def fmt(d: date) -> str:
    """Format date as dd/mm/yyyy for display."""
    return d.strftime("%d/%m/%Y")
