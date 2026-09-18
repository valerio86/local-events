"""Source registry. Adding a source is one entry here.

`default_location` is used when an event has no location of its own, which is
the norm for single-venue calendars like a library's.
"""

from . import events_manager, ics, manual, squarespace, tribe

SOURCES = {
    "catskill-mountain-club": {
        "name": "Catskill Mountain Club",
        "home": "https://www.catskillmountainclub.org/events-all",
        "url": "https://www.catskillmountainclub.org/events-all",
        "fetch": squarespace.fetch,
        # Locations live in the description; place names come from the title.
        "locate_from_title": True,
    },
    "great-western-catskills": {
        "name": "Great Western Catskills",
        "home": "https://greatwesterncatskills.com/events/",
        "url": "https://tockify.com/api/feeds/ics/greatwesterncatskills",
        "fetch": ics.fetch,
    },
    "cannon-free-library": {
        "name": "Cannon Free Library (Delhi)",
        "home": "https://libraries.4cls.org/delhi/",
        "url": "https://libraries.4cls.org/delhi/?plugin=all-in-one-event-calendar"
        "&controller=ai1ec_exporter_controller&action=export_events",
        "fetch": ics.fetch,
        "default_location": "Cannon Free Library, 40 Elm Street, Delhi, NY",
    },
    "huntington-library-programs": {
        "name": "Huntington Memorial Library (Oneonta)",
        "home": "https://hmloneonta.org/calendar/",
        "url": "https://calendar.google.com/calendar/ical/"
        "ijtpa1kf6a3deouf1mn1ms6mhg%40group.calendar.google.com/public/basic.ics",
        "fetch": ics.fetch,
        "default_location": "Huntington Memorial Library, 62 Chestnut Street, Oneonta, NY",
    },
    "bushel": {
        "name": "Bushel Collective (Delhi)",
        "home": "https://www.bushelcollective.org/events/",
        "url": "https://www.bushelcollective.org/events/",
        "fetch": events_manager.fetch,
        "default_location": "Bushel, 106 Main Street, Delhi, NY",
    },
    "bainbridge-chamber": {
        "name": "Bainbridge Chamber of Commerce",
        "home": "https://www.bainbridgecofc.com/events/",
        "url": "https://www.bainbridgecofc.com/wp-json/tribe/events/v1/events",
        "fetch": tribe.fetch,
        "default_location": "Bainbridge, NY",
    },
    "hand-entered": {
        "name": "Entered by hand (markets, Bainbridge Town Hall Theatre)",
        "home": "",
        "url": "",
        "fetch": manual.fetch,
    },
}
