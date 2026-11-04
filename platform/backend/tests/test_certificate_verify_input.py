"""Input validation for public certificate verification.

Certificate IDs are generated from ASCII track slugs and hex digests. The
verification route must reject punctuation, whitespace, kanji, emoji,
fullwidth characters, and non-ASCII digits before doing any database work.
"""
from urllib.parse import quote

import pytest

from app.routers.curriculum import parse_certificate_id


INVALID_CERTIFICATE_IDS = [
    "OCR-WEB-L01-ABCDEF0123!",           # punctuation
    "OCR-WEB-L01-ABCDEF0123<script>",    # markup
    "OCR-WEB-L01-ABCDEF0123 ",           # trailing whitespace
    " OCR-WEB-L01-ABCDEF0123",           # leading whitespace
    "OCR-WEB-L01-ABCDEF0123😀",           # emoji
    "OCR-🥷-L01-ABCDEF0123",              # emoji in the track prefix
    "OCR-ウェブ-L01-ABCDEF0123",          # kanji
    "ＯＣＲ-WEB-L01-ABCDEF0123",          # fullwidth Latin
    "OCR-WEB-L٠١-ABCDEF0123",            # Arabic-Indic digits
    "OCR-WEB-L०१-ABCDEF0123",            # Devanagari digits
]


def test_parse_certificate_id_accepts_generated_shape():
    match = parse_certificate_id("OCR-HIGH-SCH-L12-ABCDEF0123")
    assert match is not None
    assert match.groups() == ("HIGH-SCH", "12", "ABCDEF0123")


@pytest.mark.parametrize("value", INVALID_CERTIFICATE_IDS)
def test_parse_certificate_id_rejects_invalid_input(value):
    assert parse_certificate_id(value) is None


def test_parse_certificate_id_rejects_overlong_input():
    assert parse_certificate_id("OCR-" + "A" * 9 + "-L01-ABCDEF0123") is None
    assert parse_certificate_id("OCR-WEB-L01-ABCDEF0123" + "A" * 200) is None


@pytest.mark.parametrize("value", INVALID_CERTIFICATE_IDS)
def test_verify_endpoint_rejects_invalid_certificate_ids(client, value):
    response = client.get(
        f"/api/exercises/verify/certificate/{quote(value, safe='')}"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid certificate ID format"
