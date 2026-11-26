"""Canonical track slugs shared by the pathway catalogue and the curriculum.

The career pathway data uses compact manifest ids (``netfor``, ``winpt``,
``linpt``, ``webpt``) while the database and ``/exercises/tracks`` use the
track slugs (``network``, ``windows``, ``linux``, ``web``). Comparing the two
without a mapping silently hides every track in the pathway.

Keep this mapping in one place. It is a name translation, not an access rule:
callers still intersect the result with the tracks the learner is allowed to
see.
"""

from __future__ import annotations

TRACK_ALIASES = {
    "netfor": "network",
    "winpt": "windows",
    "linpt": "linux",
    "webpt": "web",
    "msfpt": "metasploit",
    "high school": "high-school",
    "software security": "software-security",
}


def canonical_track_slug(value: str | None) -> str:
    """Return the database track slug for a manifest or display name."""
    slug = str(value or "").strip().lower()
    return TRACK_ALIASES.get(slug, slug)


def canonical_track_slugs(values) -> list[str]:
    """Translate and de-duplicate a pathway's track list, preserving order."""
    return list(
        dict.fromkeys(
            canonical_track_slug(value)
            for value in (values or [])
            if str(value or "").strip()
        )
    )
