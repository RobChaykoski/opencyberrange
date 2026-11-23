"""Cloudflare dynamic DNS behaviour and safety rails."""

import pytest

from app.services import ddns


class _Response:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_domains_accepts_commas_and_spaces_and_dedupes():
    assert ddns.domains("Range.Example.edu, vpn.example.edu  range.example.edu") == [
        "range.example.edu",
        "vpn.example.edu",
    ]


@pytest.mark.parametrize(
    "value",
    ["*", "*.example.edu", "https://example.edu", "bad name", "a..b"],
)
def test_domains_rejects_wildcards_urls_and_malformed_names(value):
    with pytest.raises(ddns.DDNSError):
        ddns.domains(value)


def test_public_ipv4_rejects_private_addresses(monkeypatch):
    monkeypatch.setattr(
        ddns.requests,
        "get",
        lambda *args, **kwargs: _Response(text="ip=192.168.1.10\n"),
    )

    with pytest.raises(ddns.DDNSError):
        ddns.public_ipv4()


def test_records_outside_the_zone_are_refused(monkeypatch):
    cfg = {
        "enabled": True,
        "token": "token",
        "zone": "example.edu",
        "domains": "range.other.test",
        "proxied": False,
        "ttl": 120,
        "interval_minutes": 5,
    }
    monkeypatch.setattr(ddns, "config", lambda db: cfg)
    monkeypatch.setattr(ddns, "public_ipv4", lambda: "203.0.113.10")

    with pytest.raises(ddns.DDNSError, match="outside the configured zone"):
        ddns.sync(object(), dry_run=True)


def test_dry_run_reports_updates_without_writing(monkeypatch):
    cfg = {
        "enabled": True,
        "token": "token",
        "zone": "example.edu",
        "domains": "range.example.edu",
        "proxied": False,
        "ttl": 120,
        "interval_minutes": 5,
    }
    calls = []

    def fake_request(method, path, token, **kwargs):
        calls.append((method, path, kwargs.get("json")))
        if path.startswith("/zones?name="):
            return {"success": True, "result": [{"id": "zone-1"}]}
        if "/dns_records?type=A" in path:
            return {
                "success": True,
                "result": [
                    {
                        "id": "record-1",
                        "content": "198.51.100.20",
                        "proxied": False,
                        "ttl": 120,
                    }
                ],
            }
        raise AssertionError(f"unexpected write: {method} {path}")

    monkeypatch.setattr(ddns, "config", lambda db: cfg)
    monkeypatch.setattr(ddns, "public_ipv4", lambda: "203.0.113.10")
    monkeypatch.setattr(ddns, "_request", fake_request)

    result = ddns.sync(object(), dry_run=True)

    assert result["ok"] is True
    assert result["updated"] == 0
    assert result["actions"] == ["update range.example.edu -> 203.0.113.10"]
    assert calls == [
        ("GET", "/zones?name=example.edu&status=active", None),
        ("GET", "/zones/zone-1/dns_records?type=A&name=range.example.edu", None),
    ]
