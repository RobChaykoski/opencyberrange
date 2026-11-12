"""Image upload hardening tests.

The profile avatar and competition logos accept a base64 data URL. These tests
pin the contract: raster formats only, signature checked before decode, and the
stored value is a fresh PNG produced from decoded pixels.
"""

import base64

import pytest

from app.services.image_validation import validate_image_data_url

# 1x1 transparent PNG.
PNG_1X1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="

PNG_URL = f"data:image/png;base64,{PNG_1X1}"


def test_valid_png_is_accepted_and_normalised():
    result = validate_image_data_url(PNG_URL, label="Avatar")
    assert result.startswith("data:image/png;base64,")
    # Re-encoding produces a real PNG, not the original bytes.
    raw = base64.b64decode(result.split(",", 1)[1])
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")


def test_svg_data_url_is_rejected():
    svg = base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>').decode()
    with pytest.raises(ValueError):
        validate_image_data_url(f"data:image/svg+xml;base64,{svg}", label="Avatar")


def test_html_disguised_as_png_is_rejected():
    payload = base64.b64encode(b"<html><script>alert(1)</script></html>").decode()
    with pytest.raises(ValueError):
        validate_image_data_url(f"data:image/png;base64,{payload}", label="Avatar")


def test_declared_type_must_match_signature():
    jpeg_declared = f"data:image/jpeg;base64,{PNG_1X1}"
    with pytest.raises(ValueError):
        validate_image_data_url(jpeg_declared, label="Avatar")


def test_oversized_payload_is_rejected():
    big = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"A" * (600 * 1024)).decode()
    with pytest.raises(ValueError):
        validate_image_data_url(f"data:image/png;base64,{big}", label="Avatar")


def test_non_image_data_url_is_rejected():
    with pytest.raises(ValueError):
        validate_image_data_url("data:text/html;base64,PGgxPmhpPC9oMT4=", label="Avatar")


def test_empty_value_is_allowed():
    assert validate_image_data_url(None) is None
    assert validate_image_data_url("") == ""
