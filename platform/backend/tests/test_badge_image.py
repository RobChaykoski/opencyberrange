"""Badge artwork regression tests."""

from __future__ import annotations

import io

from PIL import Image

from app.services.badge_image import badge_png


def test_badge_png_is_a_square_png():
    data = badge_png("Linux Reconnaissance", subtitle="Level credential", footer="ABCD1234")
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    image = Image.open(io.BytesIO(data))
    assert image.size == (512, 512)
    assert image.mode == "RGB"


def test_event_badge_uses_event_artwork():
    data = badge_png(
        "Adversary Quest - First Place",
        subtitle="Event award",
        kind="event",
    )
    image = Image.open(io.BytesIO(data))
    assert image.size == (512, 512)
