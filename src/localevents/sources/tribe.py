"""WordPress sites running The Events Calendar, read through its REST API.

The API gives clean fields including a venue with a street address, which is
better than the plugin's `?ical=1` export (empty on some installs).
"""

from __future__ import annotations

import html
import re
from datetime import date, datetime

import httpx

from ..model import TZ, Event


def _text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def fetch(url: str, source: str, start: date, end: date, client: httpx.Client) -> list[Event]:
    resp = client.get(url, params={
        "per_page": 50, "start_date": start.isoformat(), "end_date": end.isoformat(),
    })
    resp.raise_for_status()

    events = []
    for item in resp.json().get("events", []):
        venue = item.get("venue") or {}
        address = ", ".join(str(p) for p in (
            venue.get("venue"), venue.get("address"), venue.get("city"), venue.get("state")) if p)
        s = datetime.fromisoformat(item["start_date"]).replace(tzinfo=TZ)
        e = datetime.fromisoformat(item["end_date"]).replace(tzinfo=TZ) if item.get("end_date") else None
        events.append(
            Event(
                title=_text(item.get("title", "")),
                start=s,
                end=e,
                all_day=bool(item.get("all_day")),
                location=address,
                url=item.get("url", ""),
                description=_text(item.get("description", "")),
                tags=[c["name"] for c in item.get("categories", [])] + [t["name"] for t in item.get("tags", [])],
                source=source,
            )
        )
    return events
