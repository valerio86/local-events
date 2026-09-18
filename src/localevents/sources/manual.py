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
    "lost-bookshop": "The Lost Bookshop, 120 Main Street, Delhi, NY",
    "dcha": "Delaware County Historical Association, 46549 State Highway 10, Delhi, NY",
    "franklin-library": "Franklin Free Library, 334 Main Street, Franklin, NY",
    "west-kortright": "West Kortright Center, 49 West Kortright Church Road, East Meredith, NY",
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

# The Lost Bookshop's site is a JavaScript app whose events API needs a browser
# session, so these were read off the page on 2026-09-18.
BOOKSHOP = "The Lost Bookshop, 120 Main St, Delhi. RSVP: hello@thelostbookshop.com"
_BOOKSHOP = [
    {"title": "Griefy Reads: Lost & Found by Kathryn Schulz", "date": date(2026, 9, 24),
     "hours": (time(18), time(19, 30)),
     "note": "Quarterly book group on grief and loss, with the Friends of Woodland Cemetery. " + BOOKSHOP},
    {"title": "Grannycakes: an intergenerational bake-off", "date": date(2026, 10, 4),
     "hours": (time(16), time(17)),
     "note": "Get matched with a Delco neighbour of another generation and bake together. " + BOOKSHOP},
    {"title": "Bang it out! Collective Admin Hour", "date": date(2026, 10, 8),
     "hours": (time(18), time(19)),
     "note": "Bring a laptop and clear the annoying to-do list together. " + BOOKSHOP},
    {"title": "Book Discussion: Strange Pictures", "date": date(2026, 10, 15),
     "hours": (time(18), time(19, 30)), "note": "A Japanese puzzle mystery. " + BOOKSHOP},
    {"title": "Tarot Readings with Jenn Johnson-Hamer", "date": date(2026, 10, 24),
     "hours": (time(15), time(17)),
     "note": "15-minute discovery readings, $25. Email to book a slot. " + BOOKSHOP},
    {"title": "Dream Circle with Rev. Michelle", "date": date(2026, 11, 5),
     "hours": (time(18), time(19, 30)), "note": "A 75-minute dream circle. " + BOOKSHOP},
    {"title": "Book Discussion: Loot", "date": date(2026, 11, 19),
     "hours": (time(18), time(19, 30)),
     "note": "An eighteenth-century heist novel. " + BOOKSHOP},
]
for e in _BOOKSHOP:
    e.update(venue="lost-bookshop", url="https://thelostbookshop.com/events")

# From the Delaware County Historical Association's 2026 calendar page, read
# 2026-09-18: https://www.dcha-ny.org/news.html
DCHA = "Delaware County Historical Association, Delhi. Reservations: 607-746-3849, dchadelhi@gmail.com"
_DCHA = [
    {"title": "Quilts Along the Delaware: 50th anniversary quilt show opens (through Sep 27)",
     "date": date(2026, 9, 19), "hours": (time(10), time(16)),
     "note": "Daily 10am-4pm to Sep 27, $5. Quilting demonstrations at weekends; raffle drawn Sep 27. " + DCHA},
    {"title": "Lackawanna coal mine and trolley museum bus trip", "date": date(2026, 9, 24),
     "hours": None,
     "note": "Guided underground tour in Scranton, PA, plus the Electric City Trolley Museum and dinner. "
             "$130 members / $150 non-members. " + DCHA},
    {"title": "Restoring Historic Stone Walls with Patrick Ryan", "date": date(2026, 10, 3),
     "hours": (time(10), time(16)),
     "note": "Two-day West Kortright Center workshop rebuilding DCHA's cemetery wall, $240. "
             "Booking through westkc.org, 607-278-5454."},
    {"title": "Restoring Historic Stone Walls with Patrick Ryan", "date": date(2026, 10, 4),
     "hours": (time(10), time(16)),
     "note": "Day two of the West Kortright Center dry-stone walling workshop, $240."},
    {"title": "Spooky Candle Workshop", "date": date(2026, 10, 10), "hours": (time(14), None),
     "venue": "franklin-library",
     "note": "Free, ages 12+, no heat involved. Arrive promptly at 2pm. " + DCHA},
    {"title": "Twilight lantern tours of the 1797 Gideon Frisbee House", "date": date(2026, 10, 24),
     "hours": (time(17), None),
     "note": "Tours leave at 5pm and 6pm, 10 people each. Adults $10, under 12 free. "
             "Reserve by Oct 23. " + DCHA},
    {"title": "DCHA annual meeting and dish-to-pass lunch", "date": date(2026, 11, 8),
     "hours": (time(13), None),
     "note": "Award of Merit presentation; the public is welcome at 2:45pm for the talk. " + DCHA},
]
for e in _DCHA:
    e.setdefault("venue", "dcha")
    e.setdefault("url", "https://www.dcha-ny.org/news.html")

# West Kortright Center's remaining autumn show. Its other listings already reach
# us through Great Western Catskills, so only the gap is entered here.
_WKC = [
    {"title": "The Saami Brothers", "date": date(2026, 9, 26), "hours": (time(19), None),
     "venue": "west-kortright", "url": "https://www.westkc.org/programs-eventz",
     "note": "Wood-fired pizza from Tara's before the show. From westkc.org, read 2026-09-18."},
]

ONE_OFF += _BOOKSHOP + _DCHA + _WKC


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
