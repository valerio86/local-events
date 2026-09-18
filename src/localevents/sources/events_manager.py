"""WordPress sites running the Events Manager plugin, read from their list view.

Events Manager publishes an `?ical=1` export, but on Bushel it has been stuck in
2020 for years, so the list view is the reliable source. It gives a date, a title
and a link per event; the start time lives on the event page, usually as the
first bold line ("Friday, September 18, 5:30-7 pm").
"""

from __future__ import annotations

import html
import re
from datetime import date, datetime, time

import httpx

from ..model import TZ, Event

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), start=1)}

ROW = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), ([A-Z][a-z]{2}) (\d{1,2})<br\s*/?>\s*"
    r'<a href="([^"]+)"[^>]*>(.*?)</a>',
    re.S,
)
# "5:30-7 pm", "7 pm", "10 am-2 pm": the meridiem may appear only at the end.
TIMES = re.compile(
    r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:[-‒-―]|to)\s*"
    r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b|\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
    re.I,
)
MAX_PAGES = 40  # be gentle with a small site


def _clean(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def _hour(h: str, m: str | None, mer: str | None) -> time:
    hour = int(h) % 12
    if (mer or "").lower() == "pm":
        hour += 12
    elif mer is None and int(h) < 8:  # a bare "5" at a village venue means 5 pm
        hour += 12
    return time(hour, int(m or 0))


def _times(page: str) -> tuple[time, time | None] | None:
    """Times are written in prose, bold or not: "6:30 - 8:00 pm", "from 4-7pm"."""
    body = re.search(r"<article>(.*?)</article>", page, re.S)
    text = _clean(body.group(1) if body else page)
    for para in [text[:800]]:
        m = TIMES.search(para)
        if not m:
            continue
        if m.group(4):  # a range
            end_mer = m.group(6)
            return _hour(m.group(1), m.group(2), m.group(3) or end_mer), _hour(m.group(4), m.group(5), end_mer)
        return _hour(m.group(7), m.group(8), m.group(9)), None
    return None


def fetch(url: str, source: str, start: date, end: date, client: httpx.Client) -> list[Event]:
    resp = client.get(url)
    resp.raise_for_status()
    body = resp.text[resp.text.find("em-events-list"):]

    rows, year, prev_month = [], start.year, start.month
    for mon, day, href, title in ROW.findall(body):
        month = MONTHS[mon]
        if month < prev_month:  # the list runs forward, so a smaller month is next year
            year += 1
        prev_month = month
        d = date(year, month, int(day))
        if start <= d < end:
            rows.append((d, href, _clean(title)))

    events = []
    seen_pages: dict[str, tuple[time, time | None] | None] = {}
    for d, href, title in rows:
        if href not in seen_pages:
            if len(seen_pages) >= MAX_PAGES:
                break
            try:
                page = client.get(href)
                seen_pages[href] = _times(page.text) if page.status_code == 200 else None
            except httpx.HTTPError:
                seen_pages[href] = None
        t = seen_pages[href]
        events.append(
            Event(
                title=title,
                start=datetime.combine(d, t[0] if t else time(0), TZ),
                end=datetime.combine(d, t[1], TZ) if t and t[1] else None,
                all_day=t is None,
                url=href,
                source=source,
                # A recurring event's URL carries every date in the series.
                series=len(re.findall(r"\d{4}-\d{2}-\d{2}", href)) > 1
                or sum(1 for r in rows if r[1] == href) > 1,
            )
        )
    return events
