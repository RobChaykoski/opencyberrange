"""Central consent enforcement for feature APIs.

Route-level checks remain as defense in depth, but this middleware is the one
place every request to a consent-gated feature passes through. A service never
has to ask "do I have consent?"; by the time it is called, consent has already
been validated.

The map is deliberately explicit. Add a path here when a new derived-data API is
introduced; do not rely on individual routers remembering to call the service.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth import _decode_token, get_user_by_username
from app.database import SessionLocal

logger = logging.getLogger(__name__)

# Longest/most specific prefixes first.
CONSENT_PATH_PREFIXES: tuple[tuple[str, str], ...] = (
    ("/api/dna", "cyber_dna"),
    ("/api/profile/skill-dna", "cyber_dna"),
    ("/api/profile/career-dossier", "cyber_dna"),
    ("/api/profile/competencies", "cyber_dna"),
    ("/api/profile/gps", "cyber_gps"),
    ("/api/profile/role-readiness", "cyber_gps"),
    ("/api/profile/portfolio", "portfolio"),
    ("/api/profile/snapshots", "portfolio"),
    ("/api/coach", "ai_coach"),
    ("/api/ai", "ai_coach"),
    ("/api/portfolio", "portfolio_sharing"),
    ("/api/research", "research"),
)


def consent_type_for_path(path: str) -> Optional[str]:
    """Return the consent domain for a protected API path, or ``None``."""
    normalized = path or ""
    for prefix, consent_type in CONSENT_PATH_PREFIXES:
        if (
            normalized == prefix
            or normalized.startswith(prefix + "/")
            or normalized.startswith(prefix + ".")
        ):
            return consent_type
    return None


def _bearer_token(request: Request) -> Optional[str]:
    header = request.headers.get("authorization") or ""
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


async def consent_enforcement(request: Request, call_next):
    """Reject a consent-gated request before its service runs.

    Missing or invalid tokens are passed through so the normal authentication
    dependency can return the correct 401. A valid token with revoked consent
    is rejected here with a stable ``ConsentRequired`` payload.
    """
    if request.method == "OPTIONS":
        return await call_next(request)

    consent_type = consent_type_for_path(request.url.path)
    if consent_type is None:
        return await call_next(request)

    token = _bearer_token(request)
    if token is None:
        return await call_next(request)

    db = SessionLocal()
    try:
        try:
            payload = _decode_token(token, db)
            # The route dependency can reuse this decode instead of validating
            # the same token again. Consent already paid for the revocation
            # lookup above.
            request.state.auth_payload = payload
            request.state.auth_revocation_checked = True
        except HTTPException:
            # Let the route's authentication dependency own the 401 response.
            return await call_next(request)

        username = payload.get("sub")
        user = get_user_by_username(db, username=username)
        if user is None:
            return await call_next(request)

        from app.consent import service as consent_service

        status = consent_service.blocked_status(db, user.id, consent_type)
        if status is None:
            return await call_next(request)

        logger.info(
            "Consent gate blocked path=%s user_id=%s type=%s status=%s",
            request.url.path,
            user.id,
            consent_type,
            status,
        )
        return JSONResponse(
            status_code=403,
            content={
                "error": "ConsentRequired",
                "detail": (
                    f"{consent_type.replace('_', ' ').title()} consent is not "
                    "granted. Re-enable it from Privacy and consent."
                ),
                "consent_type": consent_type,
                "consent_status": status,
            },
            headers={"X-Consent-Status": status},
        )
    except Exception:
        logger.exception("Consent enforcement failed closed for %s", request.url.path)
        return JSONResponse(
            status_code=503,
            content={
                "error": "ConsentCheckUnavailable",
                "detail": "Consent enforcement is temporarily unavailable.",
            },
        )
    finally:
        db.close()
