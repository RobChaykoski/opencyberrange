"""Deterministic PNG badge artwork for hosted Open Badges credentials."""

from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager


NAVY = (10, 18, 35)
NAVY_LIGHT = (18, 31, 55)
ACCENT = (56, 189, 248)
GOLD = (245, 158, 11)
TEXT = (241, 245, 249)
MUTED = (148, 163, 184)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    family = "DejaVu Sans"
    path = font_manager.findfont(
        font_manager.FontProperties(family=family, weight="bold" if bold else "normal")
    )
    return ImageFont.truetype(path, size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = str(text or "").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]


def badge_png(
    title: str,
    *,
    subtitle: str = "SWOCTS Cyber Range",
    footer: str = "",
    kind: str = "level",
    size: int = 512,
) -> bytes:
    """Render a square credential badge as PNG bytes.

    The design is deliberately dependency-free at request time: a navy field,
    a shield, the achievement title, and the issuer. It is deterministic for a
    given title/subtitle so caches and previews stay stable.
    """
    image = Image.new("RGB", (size, size), NAVY)
    draw = ImageDraw.Draw(image)

    # Soft vertical field.
    for y in range(size):
        mix = y / max(size - 1, 1)
        color = tuple(
            int(NAVY[i] + (NAVY_LIGHT[i] - NAVY[i]) * mix) for i in range(3)
        )
        draw.line([(0, y), (size, y)], fill=color)

    margin = int(size * 0.08)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=int(size * 0.06),
        outline=ACCENT if kind != "event" else GOLD,
        width=max(2, size // 128),
    )

    # Shield mark.
    cx, cy = size // 2, int(size * 0.29)
    w, h = int(size * 0.16), int(size * 0.20)
    shield = [
        (cx, cy - h // 2),
        (cx + w // 2, cy - h // 3),
        (cx + w // 2, cy + h // 6),
        (cx, cy + h // 2),
        (cx - w // 2, cy + h // 6),
        (cx - w // 2, cy - h // 3),
    ]
    draw.polygon(shield, outline=ACCENT if kind != "event" else GOLD, width=max(2, size // 160))

    title_font = _font(int(size * 0.062), bold=True)
    body_font = _font(int(size * 0.038))
    small_font = _font(int(size * 0.030), bold=True)

    y = int(size * 0.47)
    lines = _wrap(draw, title, title_font, int(size * 0.78))
    for line in lines:
        box = draw.textbbox((0, 0), line, font=title_font)
        draw.text(
            ((size - (box[2] - box[0])) / 2, y),
            line,
            font=title_font,
            fill=TEXT,
        )
        y += int(size * 0.075)

    y += int(size * 0.015)
    subtitle_lines = _wrap(draw, subtitle, body_font, int(size * 0.76))
    for line in subtitle_lines:
        box = draw.textbbox((0, 0), line, font=body_font)
        draw.text(
            ((size - (box[2] - box[0])) / 2, y),
            line,
            font=body_font,
            fill=MUTED,
        )
        y += int(size * 0.050)

    # Footer band.
    band_top = int(size * 0.84)
    draw.rectangle([margin, band_top, size - margin, size - margin], fill=NAVY)
    draw.text(
        (margin + int(size * 0.03), band_top + int(size * 0.035)),
        "SWOCTS",
        font=small_font,
        fill=ACCENT if kind != "event" else GOLD,
    )
    if footer:
        footer_font = _font(int(size * 0.025))
        text_width = draw.textlength(footer, font=footer_font)
        draw.text(
            (size - margin - int(size * 0.03) - text_width, band_top + int(size * 0.042)),
            footer[:44],
            font=footer_font,
            fill=MUTED,
        )

    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()
