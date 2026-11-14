"""Level certificate PDF layout checks that do not need a database."""

import re

from app.routers.curriculum import CERTIFICATE_DESIGNS, _certificate_pdf_bytes


def _certificate(design: str) -> dict:
    return {
        "kind": "level",
        "recipient": "Test Learner",
        "level_number": 3,
        "level_name": "Identity and Access Management",
        "track_name": "CompTIA Security+",
        "exercises_completed": 5,
        "exercises_total": 5,
        "issued_display": "14 November 2026",
        "certificate_id": "OCR-LVL-1-3-ABCDEF0123",
        "public_verification": True,
        "verify_url": (
            "https://ctfd.swocts.com/verify/certificate/"
            "OCR-LVL-1-3-ABCDEF0123"
        ),
        "achievements": [
            {"label": "First Blood", "count": 1},
            {"label": "Self-Reliant", "count": 2},
        ],
        "design": design,
        "qr_code": None,
    }


def _stable(pdf: bytes) -> bytes:
    """Drop the render timestamp so two renders can be compared."""
    return re.sub(rb"/CreationDate \(.*?\)", b"", pdf)


def test_each_design_renders_a_distinct_a4_landscape_pdf():
    outputs = {
        design: _certificate_pdf_bytes(_certificate(design))
        for design in CERTIFICATE_DESIGNS
    }

    assert len(set(_stable(pdf) for pdf in outputs.values())) == len(
        CERTIFICATE_DESIGNS
    )

    for design, pdf in outputs.items():
        assert pdf.startswith(b"%PDF"), design

        media_box = re.search(
            rb"/MediaBox\s*\[\s*0(?:\.0+)?\s+0(?:\.0+)?\s+([0-9.]+)\s+([0-9.]+)\s*\]",
            pdf,
        )
        assert media_box, f"{design} PDF has no MediaBox"
        width_pt, height_pt = (float(value) for value in media_box.groups())
        # A4 is 210 x 297 mm; landscape is 841.89 x 595.28 pt.
        assert abs(width_pt - 841.89) < 1, design
        assert abs(height_pt - 595.28) < 1, design


def test_unknown_design_falls_back_to_classic():
    classic = _certificate_pdf_bytes(_certificate("classic"))
    fallback = _certificate_pdf_bytes(_certificate("not-a-design"))
    assert _stable(classic) == _stable(fallback)
