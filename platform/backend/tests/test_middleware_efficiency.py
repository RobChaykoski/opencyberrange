"""RB-02: a request must not decode its bearer token more than once.

Middleware and the route dependency share ``request.state.auth_payload``.
This regression test counts real decodes, so a new middleware that re-inspects
the token is caught instead of silently multiplying the work.
"""

from __future__ import annotations

import pytest

import app.auth as auth_module

pytestmark = pytest.mark.db


def _counting_decode(monkeypatch):
    calls: list[str] = []
    original = auth_module._decode_token

    def wrapper(token, *args, **kwargs):
        calls.append(token)
        return original(token, *args, **kwargs)

    monkeypatch.setattr(auth_module, "_decode_token", wrapper)
    return calls


def test_read_request_decodes_the_token_once(client, auth_headers, monkeypatch):
    calls = _counting_decode(monkeypatch)

    response = client.get("/api/auth/settings", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert len(calls) == 1


def test_mutating_request_decodes_the_token_once(client, auth_headers, monkeypatch):
    # The impersonation guard decodes mutating requests before routing; the
    # route dependency must reuse that payload, not decode again. The session
    # is absent, so the route answers 404 after authentication.
    calls = _counting_decode(monkeypatch)

    response = client.delete("/api/auth/sessions/nonexistent-session", headers=auth_headers)

    assert response.status_code in (403, 404), response.text
    assert len(calls) == 1
