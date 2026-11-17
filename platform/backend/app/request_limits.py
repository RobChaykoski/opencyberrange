"""Request body size limits.

The platform accepts a few deliberately large uploads (lab sources, workbook
archives, and a database restore snapshot). Everything else is JSON or form
input and does not need more than a few megabytes. Enforcing the limit per route
keeps an accidental or hostile multi-gigabyte body from being buffered by the
application while still allowing the upload paths that need the room.

Nginx has its own ``client_max_body_size``. Keep the nginx ceiling at or above
the largest route limit below; this module is the layer that distinguishes the
upload routes from ordinary API traffic.
"""

from __future__ import annotations

import json

DEFAULT_MAX_BODY_BYTES = 10 * 1024 * 1024

# Path prefixes are matched longest-first so a specific upload route cannot be
# shadowed by a shorter parent path.
_ROUTE_LIMITS: tuple[tuple[str, int], ...] = (
    ("/api/admin/system/restore/upload", 520 * 1024 * 1024),
    ("/api/admin/labs/import", 55 * 1024 * 1024),
    ("/api/admin/workbook/upload", 55 * 1024 * 1024),
    ("/api/instructor/labs/upload", 30 * 1024 * 1024),
    ("/api/reports/verify", 30 * 1024 * 1024),
    ("/api/admin/users/import", 25 * 1024 * 1024),
)


def max_body_bytes(path: str) -> int:
    """Return the body-size cap for an API path."""
    for prefix, limit in _ROUTE_LIMITS:
        if path == prefix or path.startswith(prefix + "/"):
            return limit
    return DEFAULT_MAX_BODY_BYTES


def _limit_label(limit: int) -> str:
    if limit % (1024 * 1024) == 0:
        return f"{limit // (1024 * 1024)} MB"
    return f"{limit // 1024} KB"


async def _send_error(send, status_code: int, detail: str) -> None:
    body = json.dumps({"detail": detail}).encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": status_code,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("ascii")),
        ],
    })
    await send({"type": "http.response.body", "body": body})


class BodySizeLimitMiddleware:
    """Reject oversized HTTP bodies by declared length and by streamed size.

    ``Content-Length`` is checked before the route runs. A chunked request has
    no declared length, so the receive channel is also counted; if the limit is
    crossed before the response starts, the client gets a 413 instead of the
    application buffering the whole body.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        limit = max_body_bytes(scope.get("path", ""))
        headers = dict(scope.get("headers") or [])
        declared = headers.get(b"content-length")

        if declared is not None:
            try:
                declared_bytes = int(declared)
            except (TypeError, ValueError):
                await _send_error(send, 400, "Invalid Content-Length header.")
                return
            if declared_bytes < 0:
                await _send_error(send, 400, "Invalid Content-Length header.")
                return
            if declared_bytes > limit:
                await _send_error(
                    send,
                    413,
                    f"Request body exceeds the {_limit_label(limit)} limit.",
                )
                return

        received = 0
        overflow = False
        response_started = False
        replaced = False

        async def limited_receive():
            nonlocal received, overflow
            message = await receive()
            if message.get("type") == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    # Stop feeding the application. Do not raise here: Starlette
                    # converts a receive error into a 400 body-parsing response,
                    # which would hide the real cause. The send wrapper below
                    # replaces that response with a 413 instead.
                    overflow = True
                    return {"type": "http.request", "body": b"", "more_body": False}
            return message

        async def tracked_send(message):
            nonlocal response_started, replaced
            if overflow and not response_started:
                response_started = True
                replaced = True
                await _send_error(
                    send,
                    413,
                    f"Request body exceeds the {_limit_label(limit)} limit.",
                )
                return
            if replaced:
                return
            if message.get("type") == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except Exception:
            if replaced:
                return
            if overflow and not response_started:
                await _send_error(
                    send,
                    413,
                    f"Request body exceeds the {_limit_label(limit)} limit.",
                )
                return
            raise

        if overflow and not response_started:
            await _send_error(
                send,
                413,
                f"Request body exceeds the {_limit_label(limit)} limit.",
            )
