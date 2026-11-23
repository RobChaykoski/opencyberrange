"""Registration attribution and conference QR tracking.

Sources are short, normalized labels. Known marketing sources are mapped to
stable values so the dashboard does not split ``linkedin`` across several
spellings; other values are sanitized and kept so future campaigns work without
a code change.
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from app.services.activity import EventTypes, log_activity

# Stable labels for the sources the platform reports explicitly.
KNOWN_SOURCES = ("gdg", "linkedin", "swocts", "direct", "unknown")
SOURCE_LABELS = {
    "gdg": "GDG",
    "linkedin": "LinkedIn",
    "swocts": "SWOCTS",
    "direct": "Direct",
    "unknown": "Unknown",
}

_SOURCE_ALIASES = {
    "google-developer-groups": "gdg",
    "google-developer-group": "gdg",
    "google-devtools": "gdg",
    "gdg-conference": "gdg",
    "linked-in": "linkedin",
    "linkedin.com": "linkedin",
    "swocts.com": "swocts",
    "swocts-community": "swocts",
    "direct-link": "direct",
    "none": "direct",
}

_SLUG_RE = re.compile(r"[^a-z0-9_-]+")


def _slug(value: Optional[str], *, fallback: str, max_length: int = 50) -> str:
    text = (value or "").strip().lower()
    text = _SLUG_RE.sub("-", text).strip("-_")
    return (text or fallback)[:max_length]


def normalize_source(value: Optional[str]) -> str:
    """Return a stable source label for a query parameter or form value."""
    raw = (value or "").strip().lower()
    if not raw:
        return "direct"
    if raw in _SOURCE_ALIASES:
        return _SOURCE_ALIASES[raw]
    slug = _slug(raw, fallback="unknown")
    return _SOURCE_ALIASES.get(slug, slug)


def normalize_campaign(value: Optional[str]) -> Optional[str]:
    """Return a sanitized campaign label, or None when unset."""
    text = (value or "").strip()
    if not text:
        return None
    return _slug(text, fallback="campaign", max_length=100)


def source_label(value: Optional[str]) -> str:
    key = normalize_source(value)
    return SOURCE_LABELS.get(key, key.replace("-", " ").title())


def qr_target(source: str, campaign: Optional[str] = None) -> str:
    """Relative public URL that records a scan and redirects to registration."""
    from app.services.sso_flow import public_base_url

    normalized_source = normalize_source(source)
    normalized_campaign = normalize_campaign(campaign)
    params = {"campaign": normalized_campaign} if normalized_campaign else {}
    query = f"?{urlencode(params)}" if params else ""
    return f"{public_base_url()}/api/public/qr/{normalized_source}{query}"


def registration_path(source: str, campaign: Optional[str] = None) -> str:
    params = {"src": normalize_source(source)}
    normalized_campaign = normalize_campaign(campaign)
    if normalized_campaign:
        params["campaign"] = normalized_campaign
    return f"/register?{urlencode(params)}"


def record_qr_scan(
    db: Session,
    *,
    source: str,
    campaign: Optional[str],
    ip_address: Optional[str],
    user_agent: Optional[str],
    path: str,
) -> None:
    """Record one QR landing before the browser is redirected to registration."""
    log_activity(
        db,
        EventTypes.QR_SCANNED,
        target_type="campaign",
        target_label=campaign or source,
        detail={
            "source": normalize_source(source),
            "campaign": normalize_campaign(campaign),
            "path": path,
            "user_agent": (user_agent or "")[:300] or None,
        },
        ip_address=ip_address,
    )
