"""Strict validation for user-supplied images.

Every image that reaches the database is a base64 data URL. Accept only the
three raster formats the UI offers (PNG, JPEG, WebP), verify the declared type
against the file signature, then let Pillow decode and verify the image. SVG is
deliberately excluded: it is a document format that can carry script.
"""

from __future__ import annotations

import base64
import binascii
import io
import re
from typing import Optional

_DATA_URL_RE = re.compile(
    r"^data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=\s]+)$",
    re.IGNORECASE,
)

_ALLOWED_FORMATS = {"png", "jpeg", "webp"}


def _normalise(kind: str) -> str:
    kind = kind.lower()
    return "jpeg" if kind == "jpg" else kind


def _magic_matches(kind: str, raw: bytes) -> bool:
    if kind == "png":
        return raw.startswith(b"\x89PNG\r\n\x1a\n")
    if kind == "jpeg":
        return raw.startswith(b"\xff\xd8\xff")
    if kind == "webp":
        return len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
    return False


def validate_image_data_url(
    value: Optional[str],
    *,
    label: str = "Image",
    max_bytes: int = 512 * 1024,
    max_pixels: int = 4_000_000,
) -> Optional[str]:
    """Return the value unchanged when it is a real raster image, else raise.

    The checks run in order: data-URL shape, base64, byte cap, file signature,
    decoded dimensions, format agreement, and a full Pillow verify. A document
    renamed to .png fails at the signature check; a mismatched signature fails
    before Pillow is asked to parse attacker-controlled bytes.
    """
    if value is None or value == "":
        return value

    match = _DATA_URL_RE.match(value)
    if not match:
        raise ValueError(f"{label} must be a PNG, JPEG, or WebP image.")

    declared = _normalise(match.group(1))
    if declared not in _ALLOWED_FORMATS:
        raise ValueError(f"{label} must be a PNG, JPEG, or WebP image.")

    try:
        raw = base64.b64decode(re.sub(r"\s+", "", match.group(2)), validate=True)
    except (binascii.Error, ValueError):
        raise ValueError(f"{label} data is not valid base64.")

    if len(raw) > max_bytes:
        raise ValueError(f"{label} must be {max_bytes // 1024} KB or smaller.")

    if not _magic_matches(declared, raw):
        raise ValueError(f"{label} content does not match its image type.")

    try:
        from PIL import Image

        with Image.open(io.BytesIO(raw)) as image:
            width, height = image.size
            if width < 1 or height < 1 or width * height > max_pixels:
                raise ValueError(f"{label} dimensions are too large.")
            if (image.format or "").lower() != declared:
                raise ValueError(f"{label} content does not match its image type.")
            if getattr(image, "is_animated", False):
                raise ValueError(f"{label} must be a single-frame image.")
            image.verify()

        # Re-encode from decoded pixels into a fresh PNG. The stored bytes are
        # produced by Pillow, never the uploader, so embedded payloads, EXIF,
        # trailing data, and polyglot tricks are discarded. PNG keeps the
        # operation lossless and stable if the same value is saved again.
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            clean = io.BytesIO()
            image.save(clean, format="PNG", optimize=True)
    except ValueError:
        raise
    except Exception:
        raise ValueError(f"{label} is not a readable image.")

    normalised = clean.getvalue()
    if len(normalised) > max_bytes:
        raise ValueError(f"{label} must be {max_bytes // 1024} KB or smaller after processing.")

    return f"data:image/png;base64,{base64.b64encode(normalised).decode('ascii')}"
