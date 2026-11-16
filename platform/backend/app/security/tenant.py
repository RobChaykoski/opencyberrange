"""Request-scoped tenant context.

The Authorization Service uses this value for object checks, and PostgreSQL RLS
uses it for tenant-scoped tables. The value always comes from the server-loaded
``User`` row, never from a client claim, query parameter, or request body.

A request that has not authenticated yet runs in the default institution, not
in system-wide mode. Background jobs have no request scope and run as the system
principal, which is how the scheduler and startup tasks retain global access.
"""

from __future__ import annotations

from contextvars import ContextVar

DEFAULT_INSTITUTION = "default"

_TENANT_ID: ContextVar[str | None] = ContextVar("ocr_tenant_id", default=None)
_SYSTEM_ADMIN: ContextVar[bool] = ContextVar("ocr_system_admin", default=False)
_REQUEST_SCOPE: ContextVar[bool] = ContextVar("ocr_request_scope", default=False)


def set_tenant(institution_id: str | None, *, system_admin: bool = False) -> None:
    _TENANT_ID.set((institution_id or "").strip() or None)
    _SYSTEM_ADMIN.set(bool(system_admin))


def get_tenant() -> tuple[str | None, bool]:
    return _TENANT_ID.get(), _SYSTEM_ADMIN.get()


def begin_request() -> None:
    _REQUEST_SCOPE.set(True)


def end_request() -> None:
    _REQUEST_SCOPE.set(False)


def in_request() -> bool:
    return _REQUEST_SCOPE.get()


def clear_tenant() -> None:
    _TENANT_ID.set(None)
    _SYSTEM_ADMIN.set(False)


def rls_identity() -> tuple[str, str]:
    """Return the ``(institution_id, system_admin)`` GUC values for a session.

    * authenticated request -> its tenant, or system-admin only for ``admin``
    * unauthenticated request -> the default institution
    * background/startup job -> system-wide
    """
    tenant, system_admin = get_tenant()
    if tenant or system_admin:
        return tenant or "", "true" if system_admin else "false"
    if in_request():
        return DEFAULT_INSTITUTION, "false"
    return "", "true"
