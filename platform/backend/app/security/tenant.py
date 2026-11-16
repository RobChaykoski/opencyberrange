"""Request-scoped tenant context.

The Authorization Service uses this value for object checks, and PostgreSQL RLS
uses it for tenant-scoped tables. The value always comes from the server-loaded
``User`` row, never from a client claim, query parameter, or request body.
"""

from __future__ import annotations

from contextvars import ContextVar

_TENANT_ID: ContextVar[str | None] = ContextVar("ocr_tenant_id", default=None)
_SYSTEM_ADMIN: ContextVar[bool] = ContextVar("ocr_system_admin", default=False)


def set_tenant(institution_id: str | None, *, system_admin: bool = False) -> None:
    _TENANT_ID.set((institution_id or "").strip() or None)
    _SYSTEM_ADMIN.set(bool(system_admin))


def get_tenant() -> tuple[str | None, bool]:
    return _TENANT_ID.get(), _SYSTEM_ADMIN.get()


def clear_tenant() -> None:
    _TENANT_ID.set(None)
    _SYSTEM_ADMIN.set(False)
