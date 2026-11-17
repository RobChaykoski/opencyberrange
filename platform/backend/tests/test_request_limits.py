"""Request body caps are route-aware and apply to declared and streamed bodies."""

from app import request_limits
from app.request_limits import BodySizeLimitMiddleware, max_body_bytes


def test_default_and_upload_route_limits():
    assert max_body_bytes("/api/auth/login") == request_limits.DEFAULT_MAX_BODY_BYTES
    assert max_body_bytes("/api/admin/system/restore/upload") == 520 * 1024 * 1024
    assert max_body_bytes("/api/admin/labs/import") == 55 * 1024 * 1024
    assert max_body_bytes("/api/instructor/labs/upload") == 30 * 1024 * 1024
    assert max_body_bytes("/api/reports/verify") == 30 * 1024 * 1024
    assert max_body_bytes("/api/admin/users/import") == 25 * 1024 * 1024


async def _collect_send(messages):
    async def send(message):
        messages.append(message)
    return send


async def test_declared_oversized_body_is_rejected_before_routing():
    called = []

    async def downstream(scope, receive, send):
        called.append(True)

    messages = []
    scope = {
        "type": "http",
        "path": "/api/auth/login",
        "headers": [(b"content-length", b"999999999")],
    }
    await BodySizeLimitMiddleware(downstream)(scope, None, await _collect_send(messages))

    assert called == []
    assert messages[0]["status"] == 413
    assert messages[0]["type"] == "http.response.start"


async def test_streamed_oversized_body_is_rejected(monkeypatch):
    monkeypatch.setattr(request_limits, "max_body_bytes", lambda path: 4)

    async def downstream(scope, receive, send):
        while True:
            message = await receive()
            if not message.get("body"):
                break

    messages = []

    async def receive():
        return {"type": "http.request", "body": b"12345", "more_body": False}

    scope = {"type": "http", "path": "/api/auth/login", "headers": []}
    await BodySizeLimitMiddleware(downstream)(scope, receive, await _collect_send(messages))

    assert messages[0]["status"] == 413


async def test_body_within_limit_reaches_the_route(monkeypatch):
    monkeypatch.setattr(request_limits, "max_body_bytes", lambda path: 8)
    seen = []

    async def downstream(scope, receive, send):
        message = await receive()
        seen.append(message["body"])
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    messages = []

    async def receive():
        return {"type": "http.request", "body": b"1234", "more_body": False}

    scope = {"type": "http", "path": "/api/auth/login", "headers": []}
    await BodySizeLimitMiddleware(downstream)(scope, receive, await _collect_send(messages))

    assert seen == [b"1234"]
    assert messages[0]["status"] == 200
