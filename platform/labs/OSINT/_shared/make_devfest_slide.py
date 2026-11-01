#!/usr/bin/env python3
"""Generate the fictional DevFest Windsor-Essex speaker slide export.

The slide is visually a normal conference export. The flag lives in the PNG
text metadata (the speaker notes), which is the lesson for the high-school
exercise. All speaker details are fictional.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
FLAG = "OCR{d3vf3st_c0mmun1ty_p0rtal}"


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


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), (11, 8, 32))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(11 + 18 * ratio),
            int(8 + 22 * ratio),
            int(32 + 40 * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)

    draw.ellipse((860, -180, 1320, 280), fill=(30, 24, 72))
    draw.ellipse((-160, 500, 360, 980), fill=(26, 20, 64))
    draw.rectangle((64, 64, width - 64, height - 64), outline=(125, 211, 252), width=2)
    draw.rectangle((92, 92, width - 92, height - 92), outline=(251, 191, 36), width=1)

    draw.text((110, 120), "DEVFEST WINDSOR-ESSEX 2026", font=font(26, True), fill=(251, 191, 36))
    draw.text((110, 158), "COMMUNITY CLOUD TRACK", font=font(15, True), fill=(183, 177, 206))

    draw.text((110, 250), "Shipping Small", font=font(58, True), fill=(244, 241, 255))
    draw.text((110, 318), "Cloud Run for Community Projects", font=font(30), fill=(125, 211, 252))

    draw.text((110, 420), "Ada Mercer", font=font(30, True), fill=(244, 241, 255))
    draw.text((110, 462), "Community Cloud Engineer · Civic Stack Co-op", font=font(18), fill=(183, 177, 206))
    draw.text((110, 500), "November 21, 2026 · Windsor, ON", font=font(18), fill=(183, 177, 206))

    draw.rounded_rectangle((110, 570, 560, 620), radius=10, outline=(58, 47, 104), width=1)
    draw.text((130, 585), "TRAINING PERSONA · ALL DETAILS FICTIONAL", font=font(14, True), fill=(183, 177, 206))

    draw.text((940, 640), "devfest.lab", font=font(14, True), fill=(125, 211, 252))

    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("Title", "Shipping Small: Cloud Run for Community Projects")
    info.add_text("Author", "Ada Mercer (fictional training persona)")
    info.add_text("Software", "DevFest Community Slide Export v1.2")
    info.add_text(
        "Description",
        "Speaker notes: the community track handoff token is "
        f"{FLAG}. Remove this note before publishing the deck.",
    )
    image.save(ASSETS / "devfest-slide.png", "PNG", optimize=True, pnginfo=info)
    print(f"wrote {ASSETS / 'devfest-slide.png'}")
    print(f"flag: {FLAG}")


if __name__ == "__main__":
    main()
