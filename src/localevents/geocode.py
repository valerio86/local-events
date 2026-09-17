"""Place text to coordinates, via OpenStreetMap Nominatim, cached in venues.json.

Events cluster at a few dozen venues, so after the first run nearly every lookup
is a cache hit. The cache is committed: a wrong coordinate can be fixed by hand
there and it sticks.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import httpx

CACHE = Path(__file__).resolve().parents[2] / "venues.json"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# Western Catskills / Susquehanna box; results outside it are wrong matches.
VIEWBOX = "-75.9,42.75,-73.9,41.8"


class Geocoder:
    def __init__(self, client: httpx.Client):
        self.client = client
        self.cache: dict[str, list[float] | None] = (
            json.loads(CACHE.read_text()) if CACHE.exists() else {}
        )
        self._last = 0.0
        self.failures = 0

    def save(self) -> None:
        CACHE.write_text(json.dumps(dict(sorted(self.cache.items())), indent=1) + "\n")

    def _query(self, q: str) -> list[float] | None:
        if q in self.cache:
            return self.cache[q]
        if self.failures >= 5:  # service is down; try again next build
            return None
        for attempt in range(3):
            # Nominatim usage policy: at most one request per second.
            time.sleep(max(0.0, 1.1 * 2**attempt - (time.monotonic() - self._last)))
            self._last = time.monotonic()
            try:
                resp = self.client.get(
                    NOMINATIM,
                    params={"q": q, "format": "json", "limit": 1, "countrycodes": "us",
                            "viewbox": VIEWBOX, "bounded": 1},
                )
                resp.raise_for_status()
                break
            except httpx.HTTPError:
                continue
        else:
            self.failures += 1
            return None  # not cached, so it is retried next build
        hits = resp.json()
        result = [round(float(hits[0]["lat"]), 5), round(float(hits[0]["lon"]), 5)] if hits else None
        self.cache[q] = result
        return result

    def locate(self, text: str) -> list[float] | None:
        """Try the full text, then drop leading parts (venue names Nominatim lacks)."""
        text = re.sub(r"\s*@\s*", ", ", text.replace("\\,", ","))
        parts = [p.strip() for p in text.split(",") if p.strip() and p.strip() != "USA"]
        for i in range(len(parts)):
            q = ", ".join(parts[i:])
            if i and len(parts) - i < 2:  # a lone "NY 13753" is not a place
                break
            if hit := self._query(q):
                return hit
        return None

    def locate_title(self, title: str) -> list[float] | None:
        """Hike titles name a peak or pond; good to a few miles, flagged approximate."""
        t = re.sub(r"^(hike|first day of)\s+", "", title.strip(), flags=re.I)
        t = re.split(r"\s+(?:via|from|-|–)\s+", t, maxsplit=1, flags=re.I)[0].strip()
        candidates = [t, re.sub(r"\s+(loop|trail|hike)$", "", t, flags=re.I)]
        # "Eagle and Haynes Mountains" -> "Eagle Mountain". A bare first name
        # ("Plateau") matches hamlets, so only retry with the feature word.
        if m := re.search(r"\b(Mountain|Pond|Lake)s\b", t):
            candidates.append(f"{re.split(r',| and ', t)[0].strip()} {m.group(1)}")
        for q in dict.fromkeys(candidates):
            if hit := self._query(f"{q}, New York"):
                return hit
        return None
