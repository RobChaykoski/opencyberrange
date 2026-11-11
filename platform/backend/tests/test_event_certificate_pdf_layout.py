"""Event certificate PDF layout checks that do not need a database.

The API test covers the eligibility and download path. This test renders the
PDF directly so the A4 landscape page size and the embedded event logo, sponsor
artwork, and QR image are checked even when no ephemeral Postgres is available.
"""
import base64
import io
import re

from app.services.event_certificates import event_certificate_pdf_bytes


def _png_data_url(width: int, height: int, colour: tuple[int, int, int, int]) -> str:
    from PIL import Image

    image = Image.new("RGBA", (width, height), colour)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def _certificate() -> dict:
    return {
        "kind": "event",
        "title": "Certificate of Participation",
        "recipient": "Test Learner",
        "body_line": "participated in",
        "event_name": "SWOCTS Test Event",
        "event_dates": "10 November 2026",
        "award_description": "Awarded for taking part in the event.",
        "event_logo": _png_data_url(160, 60, (59, 130, 246, 255)),
        "sponsors": [
            {
                "name": "Gold Sponsor",
                "tier": "gold",
                "logo_data": _png_data_url(120, 40, (212, 175, 55, 255)),
            },
            {
                "name": "Silver Sponsor",
                "tier": "silver",
                "logo_data": _png_data_url(120, 40, (192, 192, 192, 255)),
            },
            {
                "name": "Bronze Sponsor",
                "tier": "bronze",
                "logo_data": _png_data_url(120, 40, (205, 127, 50, 255)),
            },
        ],
        "issued_display": "11 November 2026",
        "certificate_id": "OCR-EVT-1-2-P-ABCDEF0123",
        "public_verification": True,
        "verify_url": (
            "https://ctfd.swocts.com/verify/certificate/"
            "OCR-EVT-1-2-P-ABCDEF0123"
        ),
        "qr_code": _png_data_url(80, 80, (17, 24, 39, 255)),
    }


def test_event_certificate_pdf_is_a4_landscape_with_artwork():
    pdf = event_certificate_pdf_bytes(_certificate())

    assert pdf.startswith(b"%PDF")

    media_box = re.search(
        rb"/MediaBox\s*\[\s*0(?:\.0+)?\s+0(?:\.0+)?\s+([0-9.]+)\s+([0-9.]+)\s*\]",
        pdf,
    )
    assert media_box, "PDF has no MediaBox"
    width_pt, height_pt = (float(value) for value in media_box.groups())
    # A4 is 210 x 297 mm; landscape is 841.89 x 595.28 pt.
    assert abs(width_pt - 841.89) < 1
    assert abs(height_pt - 595.28) < 1

    # One event logo, three sponsor logos, and the QR code.
    image_count = len(re.findall(rb"/Subtype\s*/Image", pdf))
    assert image_count >= 5, f"expected at least 5 embedded images, found {image_count}"
