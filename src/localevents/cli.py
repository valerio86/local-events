"""`localevents build`: fetch every source, normalize, locate, write the site."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timedelta
from importlib.resources import files
from pathlib import Path

import httpx
import typer

from . import feeds
from .categorize import CATEGORIES, categorize
from .geocode import Geocoder
from .model import TZ, Event
from .sources import SOURCES

app = typer.Typer(add_completion=False, no_args_is_help=True)

TOWNS = {
    "Bainbridge": [42.2934, -75.4796],
    "Oneonta": [42.4529, -75.0638],
    "Delhi": [42.2781, -74.9160],
}


@app.callback()
def main() -> None:
    """Local events around Bainbridge, Oneonta and Delhi, NY."""


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


@app.command()
def build(
    out: Path = typer.Option(Path("site"), help="Output directory"),
    days: int = typer.Option(60, help="Days ahead to include"),
    past: int = typer.Option(7, help="Days back to keep in feeds"),
) -> None:
    """Fetch all sources and write index.html, events.json and .ics feeds."""
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.now(TZ).date()
    start, end = today - timedelta(days=past), today + timedelta(days=days)
    client = httpx.Client(
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": "local-events/0.1 (+https://github.com/valerio86/local-events)"},
    )

    report = []
    raw: list[Event] = []
    for key, src in SOURCES.items():
        try:
            got = src["fetch"](src["url"], key, start, end, client)
            error = None
        except Exception as exc:  # one broken site must not sink the rest
            got, error = [], f"{type(exc).__name__}: {exc}"[:200]
        for ev in got:
            ev.location = ev.location or src.get("default_location", "")
        raw += got
        report.append({"key": key, "name": src["name"], "home": src["home"],
                       "fetched": len(got), "kept": 0, "error": error})
        typer.echo(f"{key:30} {len(got):4} events" + (f"  ERROR {error}" if error else ""))

    kept: dict[tuple, Event] = {}
    dropped = 0
    for ev in sorted(raw, key=lambda e: e.start):
        cat = categorize(ev)
        if cat is None:
            dropped += 1
            continue
        ev.category = cat
        k = (_norm(ev.title), ev.start.strftime("%Y%m%d%H%M"))
        if k in kept:  # same event listed by two sources: keep the first
            continue
        ev.uid = hashlib.sha1(f"{ev.source}|{ev.title}|{ev.start.isoformat()}".encode()).hexdigest()[:16]
        kept[k] = ev
    events = list(kept.values())

    geo = Geocoder(client)
    try:
        for ev in events:
            src = SOURCES[ev.source]
            # Library feeds give a room ("3rd Floor Study"); fall back to the building.
            hit = None
            for text in (ev.location, src.get("default_location")):
                if text and (hit := geo.locate(text)):
                    break
            if hit is None and src.get("locate_from_title"):
                hit = geo.locate_title(ev.title)
                ev.geo_approx = hit is not None
            if hit:
                ev.lat, ev.lon = hit
    finally:
        geo.save()

    for r in report:
        r["kept"] = sum(e.source == r["key"] for e in events)
    counts = feeds.write(events, out)

    payload = {
        "generated": datetime.now(TZ).isoformat(timespec="minutes"),
        "today": today.isoformat(),
        "window": [start.isoformat(), end.isoformat()],
        "towns": TOWNS,
        "categories": CATEGORIES,
        "feeds": counts,
        "sources": report,
        "events": [e.to_json() for e in events],
    }
    blob = json.dumps(payload, separators=(",", ":"))
    (out / "events.json").write_text(blob)
    template = files("localevents").joinpath("templates/index.html").read_text()
    # Inlined so the page also works opened straight from disk.
    (out / "index.html").write_text(template.replace("/*__DATA__*/null", blob.replace("</", "<\\/")))

    located = sum(e.lat is not None for e in events)
    typer.echo(
        f"\n{len(raw)} fetched, {dropped} dropped as non-events, {len(events)} kept, "
        f"{located} located ({sum(e.geo_approx for e in events)} approximate) → {out}/"
    )


if __name__ == "__main__":
    app()
