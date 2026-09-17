# Around Here

Events around Bainbridge, Oneonta and Delhi, NY, collected from local calendars
every morning and published as a map and as calendar feeds anyone can subscribe to.

**Page:** https://valerio86.github.io/local-events/

**Feeds:** `all.ics`, `culture.ics`, `crafts.ics`, `outdoors.ics`, `markets.ics`,
`family.ics`, `other.ics` at the same address. In Google Calendar: *Other
calendars → From URL*. Google re-checks subscribed feeds on its own schedule,
roughly daily.

## How it works

```
sources/ ──► categorize ──► dedupe ──► geocode ──► site/
 Squarespace JSON   keyword    same title   Nominatim,   index.html (map + timeline)
 iCalendar feeds    rules      + start      cached in    events.json
 hand-entered                  time         venues.json  <category>.ics
```

A GitHub Action runs `localevents build` daily at 06:15 and deploys `site/` to
GitHub Pages.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
```

```bash
.venv/bin/localevents build          # writes site/
```

```bash
open site/index.html
```

## Sources

| Source | How it's read | Covers |
|---|---|---|
| Catskill Mountain Club | Squarespace `?format=json` | Hikes; located approximately from the title |
| Great Western Catskills | Tockify iCalendar feed | Delaware County regional listings |
| Cannon Free Library, Delhi | All-in-One Event Calendar export | Library programs |
| Huntington Memorial Library, Oneonta | Public Google Calendar | Library programs, including Oneonta Farmers Market |
| Farmers markets | `sources/manual.py` | Delhi (Wed) and Oneonta (Sat), with seasonal locations |

Adding a source is one entry in `src/localevents/sources/__init__.py`. Many small
sites have a feed they don't advertise: try `?format=json` on Squarespace, the
All-in-One Event Calendar export URL on WordPress, and the `src=` of any embedded
Google Calendar (`calendar.google.com/calendar/ical/<id>/public/basic.ics`).

## Known gaps

- **Bainbridge** has no usable source yet. The town calendar feed is only planning
  board meetings, and the library has no online calendar.
- **Hike locations** are guessed from the title. The meeting place is in the
  description, which needs an LLM to read reliably.
- **Categories** are keyword rules in `categorize.py`; misfiles are fixed there.
- A wrong venue coordinate can be corrected by hand in `venues.json`.
