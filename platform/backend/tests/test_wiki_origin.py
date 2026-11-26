"""Default workbook origin for the TLS :8443 split."""

from __future__ import annotations

import json

from starlette.requests import Request

from app.routers import public_config as public_config_router
from app.services import wiki_origin


def _request(headers=None, scheme="http", path="/api/config/public"):
    raw_headers = [
        (name.lower().encode("latin-1"), value.encode("latin-1"))
        for name, value in (headers or {}).items()
    ]
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": scheme,
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": raw_headers,
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
        }
    )


def _split_request(host="ctfd.example.edu", origin=None):
    return _request(
        {
            "host": host,
            "x-forwarded-proto": "https",
            "x-forwarded-host": host,
            "x-ocr-wiki-split-origin": origin or f"https://{host}:8443",
        },
        scheme="https",
    )


def test_split_origin_uses_the_announced_8443_origin():
    assert (
        wiki_origin.split_origin(_split_request())
        == "https://ctfd.example.edu:8443"
    )


def test_split_origin_must_match_the_request_host():
    request = _split_request(origin="https://attacker.example:8443")

    assert wiki_origin.split_origin(request) == ""


def test_split_origin_requires_the_wiki_port_and_https():
    assert (
        wiki_origin.split_origin(
            _split_request(origin="https://ctfd.example.edu:9443")
        )
        == ""
    )
    assert (
        wiki_origin.split_origin(
            _split_request(origin="http://ctfd.example.edu:8443")
        )
        == ""
    )
    # A plain-HTTP request cannot turn on the split, even with the header.
    assert (
        wiki_origin.split_origin(
            _request(
                {
                    "host": "ctfd.example.edu",
                    "x-ocr-wiki-split-origin": "https://ctfd.example.edu:8443",
                }
            )
        )
        == ""
    )


def test_app_origin_is_the_https_request_origin():
    assert (
        wiki_origin.app_origin(_split_request())
        == "https://ctfd.example.edu"
    )
    assert wiki_origin.app_origin(_request({"host": "ctfd.example.edu"})) == ""
    assert (
        wiki_origin.app_origin(
            _request(
                {"host": "ctfd.example.edu:8443", "x-forwarded-proto": "https"},
                scheme="https",
            )
        )
        == "https://ctfd.example.edu:8443"
    )


def _patch_settings(monkeypatch, wiki_origin_value=""):
    def fake_setting(db, key, default=""):
        if key == "wiki_origin":
            return wiki_origin_value
        if key == "require_approval":
            return "true"
        return default

    monkeypatch.setattr(public_config_router, "get_setting_fresh", fake_setting)


def test_public_config_derives_the_split_origin_when_unset(monkeypatch):
    _patch_settings(monkeypatch)

    response = public_config_router.public_config(_split_request(), db=object())

    assert json.loads(response.body)["wiki_origin"] == "https://ctfd.example.edu:8443"


def test_public_config_prefers_the_saved_origin(monkeypatch):
    _patch_settings(monkeypatch, wiki_origin_value="https://wiki.example.edu")

    response = public_config_router.public_config(_split_request(), db=object())

    assert json.loads(response.body)["wiki_origin"] == "https://wiki.example.edu"


def test_public_config_keeps_the_same_origin_fallback(monkeypatch):
    _patch_settings(monkeypatch)

    response = public_config_router.public_config(
        _request({"host": "ctfd.example.edu"}), db=object()
    )

    assert json.loads(response.body)["wiki_origin"] == ""
