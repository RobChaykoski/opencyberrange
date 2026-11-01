#!/usr/bin/env python3
"""Generate the Kestrel Ridge badge image used by the OSINT image lab.

The clean image is a normal employee badge. The stego image is visually
identical but carries the lab flag in the least significant bit of the blue
channel, prefixed with OCRSTEG and a 4-byte length.

Run from this directory with Pillow available:

    python3 make_badge.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
FLAG = "OCR{lsb_st3g0_h1d3s_1n_pl41n_s1ght}"
MAGIC = b"OCRSTEG"
SIZE = (720, 440)


def font(size: int, bold: bool = False):
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_centered(draw, box, text, fnt, fill):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=fnt)
    x = (box[0] + box[2] - (right - left)) / 2 - left
    y = (box[1] + box[3] - (bottom - top)) / 2 - top
    draw.text((x, y), text, font=fnt, fill=fill)


def make_image():
    width, height = SIZE
    image = Image.new("RGB", SIZE, (10, 20, 31))
    draw = ImageDraw.Draw(image)

    # Vertical gradient.
    top = (12, 27, 43)
    bottom = (20, 48, 66)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(
            int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3)
        )
        draw.line([(0, y), (width, y)], fill=color)

    # Faint security grid and diagonal accent.
    for x in range(0, width, 24):
        draw.line([(x, 0), (x, height)], fill=(28, 56, 74), width=1)
    for y in range(0, height, 24):
        draw.line([(0, y), (width, y)], fill=(28, 56, 74), width=1)
    draw.polygon(
        [(0, height), (0, height - 120), (260, height)],
        fill=(16, 35, 51),
    )
    draw.polygon(
        [(width, 0), (width - 220, 0), (width, 110)],
        fill=(18, 38, 54),
    )

    # Card border.
    draw.rounded_rectangle(
        (24, 24, width - 24, height - 24),
        radius=20,
        outline=(245, 199, 106),
        width=3,
    )
    draw.rounded_rectangle(
        (34, 34, width - 34, height - 34),
        radius=15,
        outline=(94, 234, 212),
        width=1,
    )

    # Header.
    draw.text((56, 52), "K E S T R E L   R I D G E", font=font(20, True), fill=(245, 199, 106))
    draw.text((56, 78), "EMPLOYEE ACCESS", font=font(12, True), fill=(148, 174, 196))

    # Avatar.
    cx, cy, r = 160, 210, 76
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(12, 32, 48), outline=(94, 234, 212), width=3)
    draw.ellipse((cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12), outline=(245, 199, 106), width=1)
    draw_centered(draw, (cx - r, cy - r, cx + r, cy + r), "DW", font(48, True), (94, 234, 212))

    # Identity block.
    draw.text((280, 132), "Dana Whitfield", font=font(38, True), fill=(232, 238, 245))
    draw.text((280, 184), "Threat Intelligence Analyst", font=font(18), fill=(174, 196, 214))
    draw.text((280, 216), "FUSION CENTER", font=font(14, True), fill=(245, 199, 106))
    draw.text((280, 246), "Building C / Remote", font=font(14), fill=(148, 174, 196))

    # Tags.
    tag_font = font(11, True)
    x = 280
    for label in ("INTERNAL", "OSINT", "BADGE PHOTO"):
        bbox = draw.textbbox((0, 0), label, font=tag_font)
        w = bbox[2] - bbox[0] + 20
        draw.rounded_rectangle((x, 282, x + w, 306), radius=12, outline=(43, 61, 80), width=1)
        draw.text((x + 10, 288), label, font=tag_font, fill=(148, 174, 196))
        x += w + 8

    # Barcode.
    bars = [3, 1, 2, 4, 1, 3, 2, 1, 4, 2, 1, 3, 1, 2, 4, 1, 3, 2, 1, 2, 3, 1, 4, 2]
    bx = 56
    for i, bar in enumerate(bars):
        if i % 2 == 0:
            draw.rectangle((bx, 340, bx + bar * 2, 382), fill=(232, 238, 245))
        bx += bar * 2 + 3
    draw.text((56, 390), "KR-0421  ·  VALID THROUGH 2026-12-31", font=font(11, True), fill=(148, 174, 196))

    # Footer note.
    draw.text((440, 390), "PROPERTY OF KESTREL RIDGE", font=font(10, True), fill=(100, 128, 150))

    return image


def encode_lsb(image: Image.Image, flag: str) -> Image.Image:
    payload = MAGIC + len(flag.encode("utf-8")).to_bytes(4, "big") + flag.encode("utf-8")
    bits = []
    for byte in payload:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)

    pixels = image.load()
    width, height = image.size
    index = 0
    for y in range(height):
        for x in range(width):
            if index >= len(bits):
                return image
            r, g, b = pixels[x, y]
            pixels[x, y] = (r, g, (b & 0xFE) | bits[index])
            index += 1

    if index < len(bits):
        raise ValueError("image is too small for the payload")
    return image


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    image = make_image()
    image.save(ASSETS / "badge_clean.png", "PNG", optimize=True)

    stego = encode_lsb(image.copy(), FLAG)
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("Description", "Kestrel Ridge employee badge - KR-0421 - Dana Whitfield")
    info.add_text("Software", "Kestrel Ridge Photo Booth v2.1")
    stego.save(ASSETS / "badge_stego.png", "PNG", optimize=True, pnginfo=info)
    print(f"wrote {ASSETS / 'badge_clean.png'}")
    print(f"wrote {ASSETS / 'badge_stego.png'}")
    print(f"flag: {FLAG}")


if __name__ == "__main__":
    main()
