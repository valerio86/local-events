"""The one shape every source is normalized into."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")


@dataclass
class Event:
    title: str
    start: datetime  # timezone-aware
    source: str  # key in sources.SOURCES
    end: datetime | None = None
    all_day: bool = False
    location: str = ""  # free text as the source gives it
    url: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)  # source's own categories
    series: bool = False  # one occurrence of a repeating event

    # Filled in by the pipeline
    uid: str = ""
    category: str = ""
    lat: float | None = None
    lon: float | None = None
    geo_approx: bool = False  # located from a place name, not an address

    def to_json(self) -> dict:
        d = asdict(self)
        d["start"] = self.start.isoformat()
        d["end"] = self.end.isoformat() if self.end else None
        d["description"] = self.description[:400]
        return d
