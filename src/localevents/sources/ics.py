"""Any iCalendar feed: Tockify, All-in-One Event Calendar, public Google Calendars."""

from __future__ import annotations

import re
from datetime import date, datetime, time

import httpx
import icalendar
import recurring_ical_events

from ..model import TZ, Event


def _aware(v) -> tuple[datetime, bool]:
    if isinstance(v, datetime):
        return (v if v.tzinfo else v.replace(tzinfo=TZ)).astimezone(TZ), False
    if isinstance(v, date):
        return datetime.combine(v, time(0), TZ), True
    raise TypeError(v)


def fetch(url: str, source: str, start: date, end: date, client: httpx.Client) -> list[Event]:
    resp = client.get(url)
    resp.raise_for_status()
    # Tockify writes calendar-level durations as "P15M", which parsers reject;
    # they are refresh hints we don't use, so drop them.
    body = re.sub(rb"^(?:REFRESH-INTERVAL|X-PUBLISHED-TTL)[:;][^\n]*\n", b"", resp.content, flags=re.M)
    cal = icalendar.Calendar.from_ical(body)

    # Which UIDs repeat, either by RRULE or by the feed listing them many times.
    counts: dict[str, int] = {}
    for comp in cal.walk("VEVENT"):
        uid = str(comp.get("UID", ""))
        counts[uid] = counts.get(uid, 0) + (2 if comp.get("RRULE") else 1)

    events = []
    for comp in recurring_ical_events.of(cal).between(start, end):
        s, all_day = _aware(comp.decoded("DTSTART"))
        e = _aware(comp.decoded("DTEND"))[0] if comp.get("DTEND") else None
        cats = comp.get("CATEGORIES")
        tags = []
        for c in cats if isinstance(cats, list) else [cats] if cats else []:
            tags += [str(t) for t in c.cats]
        events.append(
            Event(
                title=str(comp.get("SUMMARY", "")).strip(),
                start=s,
                end=e,
                all_day=all_day,
                location=str(comp.get("LOCATION", "")).strip(),
                url=str(comp.get("URL", "")).strip(),
                description=str(comp.get("DESCRIPTION", "")).strip(),
                tags=tags,
                series=counts.get(str(comp.get("UID", "")), 0) > 1,
                source=source,
            )
        )
    return events
