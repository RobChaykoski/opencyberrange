"""Shared compliance guard for data exports.

Exports of personal or account data leave the platform's control, so the
operator must state why the export is needed. The reason is written to the
audit log alongside the export record.
"""
from fastapi import HTTPException, Query

MIN_EXPORT_REASON_LENGTH = 5
MAX_EXPORT_REASON_LENGTH = 500


def require_export_reason(
    reason: str = Query(
        ...,
        min_length=MIN_EXPORT_REASON_LENGTH,
        max_length=MAX_EXPORT_REASON_LENGTH,
        description="Why this export is needed (recorded in the audit log)",
    ),
) -> str:
    cleaned = reason.strip()
    if len(cleaned) < MIN_EXPORT_REASON_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                "A reason of at least "
                f"{MIN_EXPORT_REASON_LENGTH} characters is required for exports."
            ),
        )
    return cleaned
