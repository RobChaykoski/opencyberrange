"""RangeBox transport detection tests."""

from __future__ import annotations

from app.routers.rangebox import _detect_rangebox_transport


class _Response:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size: int = -1) -> bytes:
        return self._body


def test_detect_kasmvnc(monkeypatch):
    seen = {}

    def fake_urlopen(url, timeout=0):
        seen["url"] = url
        seen["timeout"] = timeout
        return _Response(b"<html><title>KasmVNC</title></html>")

    monkeypatch.setattr(
        "app.routers.rangebox.urllib.request.urlopen", fake_urlopen
    )
    assert _detect_rangebox_transport("10.0.0.5") == "kasm"
    assert ":6080/vnc.html" in seen["url"]


def test_detect_novnc(monkeypatch):
    monkeypatch.setattr(
        "app.routers.rangebox.urllib.request.urlopen",
        lambda *_args, **_kwargs: _Response(b"<html><title>noVNC</title></html>"),
    )
    assert _detect_rangebox_transport("10.0.0.5") == "novnc"


def test_detect_without_container_or_on_error(monkeypatch):
    assert _detect_rangebox_transport(None) is None

    def fail(*_args, **_kwargs):
        raise OSError("unreachable")

    monkeypatch.setattr("app.routers.rangebox.urllib.request.urlopen", fail)
    assert _detect_rangebox_transport("10.0.0.5") is None
