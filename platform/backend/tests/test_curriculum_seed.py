"""The seeded curriculum must cover every level the lab tree ships.

Discovery skips a lab when its (track, level) pair is absent from the database.
A new pathway can therefore add labs that never register until the seed is
updated. This guards the AD and modern-appsec level-11 pathways specifically.
"""

from __future__ import annotations

from app.scripts.seed_curriculum import EXTRA_LEVELS, TRACKS


def _seeded_levels() -> set[tuple[str, int]]:
    levels = {
        (track["slug"], int(level["level_number"]))
        for track in TRACKS
        for level in track.get("levels", [])
    }
    levels |= {
        (entry["track_slug"], int(entry["level_number"]))
        for entry in EXTRA_LEVELS
    }
    return levels


def test_level_eleven_exists_for_ad_and_appsec_pathways():
    levels = _seeded_levels()
    assert ("windows", 11) in levels
    assert ("web", 11) in levels
