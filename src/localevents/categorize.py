"""Keyword rules for category, and for dropping events nobody would subscribe to.

First matching rule wins, so order matters: a pottery *class* is crafts, not
culture; a family *movie* is family, not culture.
"""

from __future__ import annotations

import re

from .model import Event

CATEGORIES = {
    "culture": "Culture",
    "crafts": "Crafts & classes",
    "outdoors": "Outdoors & sports",
    "markets": "Markets & farms",
    "family": "Kids & family",
    "other": "Other",
}

RULES = [
    ("markets", r"farmers.?market|\bmarket\b|antiques|vintage|u-pick|farm day|flea|bazaar|harvest fest"),
    ("crafts", r"pottery|ceramic|paint with|blacksmith|knit|stitch|crochet|quilt|sewing|weav|craft|art.?class|workshop|painting class|woodworking"),
    ("family", r"story ?(time|hour)|homeschool|discovery den|toddler|preschool|pre-k|lap ?sit|tiny tots|kids|children|minecraft|teen|youth|family|afternoon (adventure|explorer)|lego"),
    ("outdoors", r"\bhike|hiking|trail|mountain|\bloop\b|\brace\b|\b\dk\b|marathon|\brun\b|bike|cycling|paddl|kayak|\bski|bird|nature|walk|long path|lark in the park|sanctuary|yoga|tai chi"),
    ("culture", r"theat|music|concert|band|\bbook|author|reading|writer|poet|film|movie|exhibit|gallery|museum|histor|lecture|\btalk\b|dance|comedy|fiddl|\bjam\b|opera|symphony|choir|art|mahjong|scrabble|board game|chess"),
]

# Administrative or services, not events.
EXCLUDE = r"^reserved|\bboard\b(?! games?)|trustees|planning|meeting of|navigator|by appt|appointment|closed|tax help|notary|\bonline\b|zoom"


def categorize(ev: Event) -> str | None:
    """Category key, or None to drop the event."""
    text = " ".join([ev.title, " ".join(ev.tags)]).lower()
    if re.search(EXCLUDE, text):
        return None
    for key, pattern in RULES:
        if re.search(pattern, text):
            return key
    # Fall back to the description, which is noisier, so only after titles fail.
    desc = ev.description[:300].lower()
    for key, pattern in RULES:
        if re.search(pattern, desc):
            return key
    return "other"
