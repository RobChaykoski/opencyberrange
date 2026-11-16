"""FastAPI policy dependencies."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.security.permissions import PolicyDecision
from app.security.policy import require_allowed


def require_permission(permission: str):
    """Authenticate, then enforce one policy permission.

    Resource scope is supplied by the route when it has a learner or course in
    hand. Routes without a resource use the policy's default scope.
    """

    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> PolicyDecision:
        return require_allowed(db, current_user, permission)

    return dependency
