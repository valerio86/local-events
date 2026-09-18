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
| Bushel Collective, Delhi | Events Manager list view, scraped | Talks, screenings, workshops, exhibitions at 106 Main St |
| Bainbridge Chamber of Commerce | The Events Calendar REST API | Bainbridge events; the calendar is empty as of Sept 2026 |
| Farmers markets | `sources/manual.py` | Delhi (Wed) and Oneonta (Sat), with seasonal locations |

Adding a source is one entry in `src/localevents/sources/__init__.py`, reusing one
of the readers in `sources/`. Many small sites have a feed they don't advertise:
try `?format=json` on Squarespace, `/wp-json/tribe/events/v1/events` for The Events
Calendar, the All-in-One Event Calendar export URL, and the `src=` of any embedded
Google Calendar (`calendar.google.com/calendar/ical/<id>/public/basic.ics`). Check
what a feed actually contains before trusting it: Bushel's `?ical=1` export returns
real iCalendar that stopped updating in 2020.

## Known gaps

- **Bainbridge** is thin. The chamber of commerce has a working feed but no events
  posted yet; the town calendar is only planning board meetings and the library has
  no online calendar. The Jericho Arts Council posts its season as images on a
  Weebly site, so reading it needs OCR.
- **Delhi shops** mostly post to Facebook. The Lost Bookshop's site is a JavaScript
  app with no feed, The Shire Pub has no site, and delhitel.com writes its listings
  as prose in WordPress pages. All three need an LLM or a browser to read.
- **Hike locations** are guessed from the title. The meeting place is in the
  description, which needs an LLM to read reliably.
- **Categories** are keyword rules in `categorize.py`; misfiles are fixed there.
- A wrong venue coordinate can be corrected by hand in `venues.json`.
