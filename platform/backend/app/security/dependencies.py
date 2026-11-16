"""FastAPI authorization dependencies."""

from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.security.permissions import PolicyDecision
from app.security.policy import require_allowed


def require_permission(permission: str):
    """Authenticate, then enforce one authorization permission.

    When the route already carries ``user_id``, ``student_id``, or ``course_id``
    in its path, the dependency passes that scope into the policy. That means a
    route cannot accidentally drop the resource owner check simply because it
    used the generic permission dependency.
    """

    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> PolicyDecision:
        resource_user_id = None
        for key in ("user_id", "student_id"):
            value = request.path_params.get(key)
            if value is not None:
                try:
                    resource_user_id = int(value)
                except (TypeError, ValueError):
                    resource_user_id = None
                break
        course_id = None
        value = request.path_params.get("course_id")
        if value is not None:
            try:
                course_id = int(value)
            except (TypeError, ValueError):
                course_id = None
        # A share token must be verified by the route before it sets this query
        # parameter; the dependency never treats a bare parameter as proof.
        shared = False
        return require_allowed(
            db,
            current_user,
            permission,
            resource_user_id=resource_user_id,
            course_id=course_id,
            shared=shared,
        )

    dependency.__permission__ = permission  # type: ignore[attr-defined]
    dependency.__name__ = f"require_permission[{permission}]"
    return dependency
