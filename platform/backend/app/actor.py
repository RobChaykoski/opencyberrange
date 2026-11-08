"""Request-scoped actor context for the database integrity ledger.

The PostgreSQL trigger cannot see the FastAPI request directly. The application
sets these values on the connection before a flush so the trigger can record who
made the change. A write with no actor context is recorded as ``system`` when it
comes from the application engine, or ``unattributed`` when it comes from a
manual client.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

_actor_type: ContextVar[Optional[str]] = ContextVar("ocr_actor_type", default=None)
_actor_id: ContextVar[Optional[int]] = ContextVar("ocr_actor_id", default=None)
_request_id: ContextVar[Optional[str]] = ContextVar("ocr_request_id", default=None)


@dataclass(frozen=True)
class ActorContext:
    actor_type: Optional[str]
    actor_id: Optional[int]
    request_id: Optional[str]


def set_actor(user=None, *, actor_type: str = "user", actor_id: Optional[int] = None) -> None:
    """Set the actor for the current request or job.

    Pass a user object when available, or explicit values for a system job.
    """
    if user is not None:
        actor_id = getattr(user, "id", actor_id)
        actor_type = "user"
    _actor_type.set(actor_type)
    _actor_id.set(actor_id)


def set_request_id(request_id: Optional[str]) -> None:
    _request_id.set(request_id or None)


def get_actor() -> ActorContext:
    return ActorContext(
        actor_type=_actor_type.get(),
        actor_id=_actor_id.get(),
        request_id=_request_id.get(),
    )


def clear_actor() -> None:
    _actor_type.set(None)
    _actor_id.set(None)
    _request_id.set(None)
