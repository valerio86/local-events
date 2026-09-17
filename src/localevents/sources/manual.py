"""Recurring events with no feed anywhere, entered once by hand."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ..model import TZ, Event

# weekday: Monday=0. `seasons` maps (first month, last month) to a location;
# ranges may wrap the year end.
MARKETS = [
    {
        "title": "Delhi Farmers' Market",
        "weekday": 2,
        "hours": (time(10), time(14)),
        "url": "https://greatwesterncatskills.com/listings/delhi-farmers-market/",
        "seasons": {
            (5, 9): "Courthouse Square, Main Street, Delhi, NY",
            (10, 4): "American Legion, 41 Page Avenue, Delhi, NY",
        },
    },
    {
        "title": "Oneonta Farmers Market",
        "weekday": 5,
        "hours": (time(9), time(12)),
        "url": "https://oneontafarmersmarket.org/",
        "seasons": {
            (5, 10): "Huntington Memorial Park, Dietz Street, Oneonta, NY",
            (11, 4): "Foothills Performing Arts Center, 24 Market Street, Oneonta, NY",
        },
    },
]


def _in_season(month: int, first: int, last: int) -> bool:
    return first <= month <= last if first <= last else month >= first or month <= last


def fetch(url: str, source: str, start: date, end: date, client=None) -> list[Event]:
    events = []
    for m in MARKETS:
        d = start + timedelta(days=(m["weekday"] - start.weekday()) % 7)
        while d < end:
            loc = next(l for (a, b), l in m["seasons"].items() if _in_season(d.month, a, b))
            events.append(
                Event(
                    title=m["title"],
                    start=datetime.combine(d, m["hours"][0], TZ),
                    end=datetime.combine(d, m["hours"][1], TZ),
                    location=loc,
                    url=m["url"],
                    tags=["farmers-market"],
                    series=True,
                    source=source,
                )
            )
            d += timedelta(days=7)
    return events
