"""Events entered by hand, for places with no feed worth scraping.

Two kinds: WEEKLY for standing dates (markets), ONE_OFF for a published season.
Each entry says where the information came from and when it was checked, so a
stale listing can be traced back and re-checked rather than guessed at.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ..model import TZ, Event

VENUES = {
    "delhi-market-summer": "Courthouse Square, Main Street, Delhi, NY",
    "delhi-market-winter": "American Legion, 41 Page Avenue, Delhi, NY",
    "oneonta-market-summer": "Huntington Memorial Park, Dietz Street, Oneonta, NY",
    "oneonta-market-winter": "Foothills Performing Arts Center, 24 Market Street, Oneonta, NY",
    "town-hall-theatre": "Bainbridge Town Hall Theatre, 15 N Main Street, Bainbridge, NY",
}

# weekday: Monday=0. `seasons` maps (first month, last month) to a venue key;
# ranges may wrap the year end.
WEEKLY = [
    {
        "title": "Delhi Farmers' Market",
        "weekday": 2,
        "hours": (time(10), time(14)),
        "url": "https://greatwesterncatskills.com/listings/delhi-farmers-market/",
        "seasons": {(5, 9): "delhi-market-summer", (10, 4): "delhi-market-winter"},
    },
    {
        "title": "Oneonta Farmers Market",
        "weekday": 5,
        "hours": (time(9), time(12)),
        "url": "https://oneontafarmersmarket.org/",
        "seasons": {(5, 10): "oneonta-market-summer", (11, 4): "oneonta-market-winter"},
    },
]

# From the Jericho Arts Council's own Fall 2026 schedule flyer, read 2026-09-18:
# https://www.jerichoarts.com/2026-fall-events.html
# Doors open at 6 pm and the gallery opens an hour before each performance.
JERICHO = "Jericho Arts Council, Fall 2026 schedule (jerichoarts.com). Reservations: 607-288-3882."
ONE_OFF = [
    {"title": "Ronstadt Rewind: Linda Ronstadt tribute", "date": date(2026, 9, 19),
     "hours": (time(19), None), "note": "All tickets $20. " + JERICHO},
    {"title": "Stuart Little, by the Out of the Woodwork Players", "date": date(2026, 10, 2),
     "hours": (time(19, 30), None), "note": "Tickets: text 607-765-5008. " + JERICHO},
    {"title": "Stuart Little, by the Out of the Woodwork Players", "date": date(2026, 10, 3),
     "hours": (time(19, 30), None), "note": "Tickets: text 607-765-5008. " + JERICHO},
    {"title": "Stuart Little, by the Out of the Woodwork Players", "date": date(2026, 10, 4),
     "hours": (time(14), None), "note": "Tickets: text 607-765-5008. " + JERICHO},
    {"title": "Blue Tonic: blues and blues-inspired rock", "date": date(2026, 10, 10),
     "hours": (time(19), None), "note": "$18 / $15. " + JERICHO},
    {"title": "Kevin Prater Band: bluegrass and old country", "date": date(2026, 10, 24),
     "hours": (time(19), None), "note": "$18 / $15. " + JERICHO},
    {"title": "Opera & Broadway Favorites", "date": date(2026, 10, 25),
     "hours": (time(15), None),
     "note": "Free admission, sponsored by the Bainbridge Free Library. " + JERICHO},
    {"title": "Cedar Ridge: bluegrass, gospel and old country", "date": date(2026, 11, 14),
     "hours": (time(19), None), "note": "$18 / $15. " + JERICHO},
    {"title": "Fifth Annual Photography Show opens (through Oct 25)", "date": date(2026, 10, 2),
     "hours": None, "note": "In the gallery, open at 6 pm before shows through intermission, free. " + JERICHO},
    {"title": "JAC Holiday Gift Market", "date": date(2026, 11, 27),
     "hours": (time(10), time(16)), "note": "Handmade gifts from regional artists. " + JERICHO},
    {"title": "JAC Holiday Gift Market", "date": date(2026, 11, 28),
     "hours": (time(10), time(16)), "note": "Handmade gifts from regional artists. " + JERICHO},
    {"title": "JAC Holiday Gift Market", "date": date(2026, 11, 29),
     "hours": (time(10), time(16)), "note": "Handmade gifts from regional artists. " + JERICHO},
]
for e in ONE_OFF:  # the whole fall season is at one venue
    e.setdefault("venue", "town-hall-theatre")
    e.setdefault("url", "https://www.jerichoarts.com/2026-fall-events.html")


def _in_season(month: int, first: int, last: int) -> bool:
    return first <= month <= last if first <= last else month >= first or month <= last


def fetch(url: str, source: str, start: date, end: date, client=None) -> list[Event]:
    events = []
    for w in WEEKLY:
        d = start + timedelta(days=(w["weekday"] - start.weekday()) % 7)
        while d < end:
            venue = next(v for (a, b), v in w["seasons"].items() if _in_season(d.month, a, b))
            events.append(
                Event(
                    title=w["title"],
                    start=datetime.combine(d, w["hours"][0], TZ),
                    end=datetime.combine(d, w["hours"][1], TZ),
                    location=VENUES[venue],
                    url=w["url"],
                    tags=["farmers-market"],
                    series=True,
                    source=source,
                )
            )
            d += timedelta(days=7)

    for o in ONE_OFF:
        if not start <= o["date"] < end:
            continue
        hours = o["hours"]
        events.append(
            Event(
                title=o["title"],
                start=datetime.combine(o["date"], hours[0] if hours else time(0), TZ),
                end=datetime.combine(o["date"], hours[1], TZ) if hours and hours[1] else None,
                all_day=hours is None,
                location=VENUES[o["venue"]],
                url=o["url"],
                description=o["note"],
                source=source,
            )
        )
    return events
