"""Stable API error codes alongside human-readable messages.

The frontend still renders ``detail`` today, so the message stays in place for
compatibility. New and migrated endpoints add an ``X-Error-Code`` header with a
stable code the client can translate. This is the first step toward
machine-readable errors without breaking existing clients.
"""

from __future__ import annotations

from fastapi import HTTPException

ERROR_CODE_HEADER = "X-Error-Code"


def api_error(
    status_code: int,
    code: str,
    message: str,
    *,
    headers: dict[str, str] | None = None,
) -> HTTPException:
    """Build an HTTPException with a stable machine-readable code."""
    merged = {ERROR_CODE_HEADER: code}
    if headers:
        merged.update(headers)
    return HTTPException(status_code=status_code, detail=message, headers=merged)
