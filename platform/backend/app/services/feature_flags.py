"""Runtime feature gates for development-only surfaces.

The platform ships one code tree to every deployment. A feature that is still
being evaluated on the development host is therefore gated by a platform
setting, not by a branch or an environment variable. The default is off so a
production install never exposes an unreviewed surface by accident.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.settings_service import get_setting_fresh

ADVANCED_DNA_INSIGHTS = "advanced_dna_insights_enabled"

_TRUTHY = {"1", "true", "yes", "on", "enabled"}


def setting_enabled(db: Session, key: str, default: str = "false") -> bool:
    """Read a boolean platform setting without the per-worker cache.

    The cache is fine for tuning values. A feature gate must see an admin's
    change immediately on every worker, so this reads the row directly.
    """
    value = get_setting_fresh(db, key, default)
    return str(value or "").strip().lower() in _TRUTHY


def advanced_dna_insights_enabled(db: Session) -> bool:
    """Return True when Momentum and Career Atlas may be shown.

    Development host only until the review in
    ``docs/CAREER-ATLAS-AND-MOMENTUM.md`` is signed off. Production keeps the
    default ``false``.
    """
    return setting_enabled(db, ADVANCED_DNA_INSIGHTS)
