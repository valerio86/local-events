"""Subscribable .ics files, one per category plus everything."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import icalendar

from .categorize import CATEGORIES
from .model import Event

NAME = "Around Here"


def _calendar(title: str, events: list[Event]) -> bytes:
    cal = icalendar.Calendar()
    cal.add("PRODID", "-//local-events//valerio86//EN")
    cal.add("VERSION", "2.0")
    cal.add("X-WR-CALNAME", title)
    cal.add("X-WR-TIMEZONE", "America/New_York")
    # A hint only; Google ignores it and polls on its own schedule.
    cal.add("REFRESH-INTERVAL", timedelta(hours=12), parameters={"VALUE": "DURATION"})
    cal.add("X-PUBLISHED-TTL", "PT12H")
    stamp = datetime.now(timezone.utc)
    for ev in events:
        v = icalendar.Event()
        v.add("UID", f"{ev.uid}@local-events")
        v.add("DTSTAMP", stamp)
        v.add("SUMMARY", ev.title)
        if ev.all_day:
            v.add("DTSTART", ev.start.date())
        else:
            v.add("DTSTART", ev.start.astimezone(timezone.utc))
            if ev.end and ev.end > ev.start:
                v.add("DTEND", ev.end.astimezone(timezone.utc))
        if ev.location:
            v.add("LOCATION", ev.location.replace("\\,", ","))
        if ev.lat is not None:
            v.add("GEO", (ev.lat, ev.lon))
        if ev.url:
            v.add("URL", ev.url)
        v.add("CATEGORIES", [CATEGORIES[ev.category]])
        v.add("DESCRIPTION", "\n\n".join(p for p in (ev.description[:1500], ev.url) if p))
        cal.add_component(v)
    return cal.to_ical()


def write(events: list[Event], out: Path) -> dict[str, int]:
    counts = {"all": len(events)}
    (out / "all.ics").write_bytes(_calendar(f"{NAME}: all events", events))
    for key, label in CATEGORIES.items():
        subset = [e for e in events if e.category == key]
        counts[key] = len(subset)
        (out / f"{key}.ics").write_bytes(_calendar(f"{NAME}: {label}", subset))
    return counts
