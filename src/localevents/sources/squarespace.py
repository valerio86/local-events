"""Squarespace event collections expose their items at `?format=json`."""

from __future__ import annotations

import html
import re
from datetime import date, datetime

import httpx

from ..model import TZ, Event


def _text(body: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body or ""))).strip()


def fetch(url: str, source: str, start: date, end: date, client: httpx.Client) -> list[Event]:
    resp = client.get(url, params={"format": "json"})
    resp.raise_for_status()
    data = resp.json()
    base = data["website"]["baseUrl"]

    events = []
    for item in data.get("upcoming", []):
        s = datetime.fromtimestamp(item["startDate"] / 1000, TZ).replace(microsecond=0)
        if not start <= s.date() < end:
            continue
        loc = item.get("location") or {}
        # Unset Squarespace locations are the site default, not a real place.
        address = ", ".join(
            p for p in (loc.get("addressTitle"), loc.get("addressLine1"), loc.get("addressLine2")) if p
        )
        events.append(
            Event(
                title=item["title"].strip(),
                start=s,
                end=datetime.fromtimestamp(item["endDate"] / 1000, TZ).replace(microsecond=0),
                location=address,
                url=base + item["fullUrl"],
                description=_text(item.get("body", "")),
                tags=item.get("categories", []) + item.get("tags", []),
                source=source,
            )
        )
    return events
