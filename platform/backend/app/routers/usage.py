"""Usage dashboard API: public aggregates and admin detail.

The public endpoints never return learner identities. They report source,
campaign, and lab aggregates and suppress small counts. The admin endpoints
return the same shape with exact counts and a CSV export.
"""

from __future__ import annotations

import csv
import io

import qrcode
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user
from app.database import get_db
from app.models import User
from app.ratelimit import create_limiter
from app.services import attribution, usage

router = APIRouter()
limiter = create_limiter()


def _json(payload: dict, *, public: bool) -> JSONResponse:
    return JSONResponse(
        payload,
        headers={
            "Cache-Control": "public, max-age=60" if public else "no-store",
        },
    )


@router.get("/public")
@limiter.limit("60/minute")
def public_usage(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Aggregate usage for the shareable tracker page."""
    return _json(usage.build_usage(db, days=days, public=True), public=True)


@router.get("/public.csv")
@limiter.limit("30/minute")
def public_usage_csv(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    payload = usage.build_usage(db, days=days, public=True)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["date", "registrations", "qr_scans", "completions"])
    for row in payload["daily"]:
        writer.writerow(
            [row["date"], row["registrations"], row["qr_scans"], row["completions"]]
        )
    return Response(
        buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="opencyberrange-usage.csv"',
            "Cache-Control": "public, max-age=60",
        },
    )


@router.get("/admin")
def admin_usage(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Exact usage detail for administrators."""
    return _json(usage.build_usage(db, days=days, public=False), public=False)


@router.get("/admin.csv")
def admin_usage_csv(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    payload = usage.build_usage(db, days=days, public=False)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "lab",
            "slug",
            "category",
            "difficulty",
            "completions",
            "learners",
            "attempts_avg",
            "hints_avg",
            "median_minutes",
            "first_attempt_rate",
            "completion_rate",
            "last_completed_at",
        ]
    )
    for row in payload["labs"]["items"]:
        writer.writerow(
            [
                row["name"],
                row["slug"],
                row["category"],
                row["difficulty"],
                row["completions"],
                row["learners"],
                row["attempts_avg"],
                row["hints_avg"],
                row["median_minutes"],
                row["first_attempt_rate"],
                row["completion_rate"],
                row["last_completed_at"],
            ]
        )
    return Response(
        buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="opencyberrange-usage-labs.csv"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/admin/qr.png")
def admin_qr_png(
    source: str = Query(..., min_length=1, max_length=50),
    campaign: str | None = Query(None, max_length=100),
    admin: User = Depends(get_current_admin_user),
):
    """Return a printable QR code for a tracked registration link."""
    target = attribution.qr_target(source, campaign)
    image = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    image.add_data(target)
    image.make(fit=True)
    buffer = io.BytesIO()
    image.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
    return Response(
        buffer.getvalue(),
        media_type="image/png",
        headers={
            "Content-Disposition": 'inline; filename="registration-qr.png"',
            "Cache-Control": "no-store",
        },
    )
