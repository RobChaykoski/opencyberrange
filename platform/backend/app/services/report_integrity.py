"""Checksum and keyed-signature protection for generated reports.

A report is only considered platform-generated when its bytes match a stored
manifest and the manifest's HMAC verifies with the server key. The key is never
sent to the browser, so a learner or instructor cannot fabricate a PDF/CSV and
make it pass verification.
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Course, ReportExport, User

_REPORT_KEY_PREFIX = "ocr-report-v1:"


def _key() -> bytes:
    secret = settings.REPORT_SIGNING_KEY or settings.JWT_SECRET
    return f"{_REPORT_KEY_PREFIX}{secret}".encode("utf-8")


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _signature(
    *,
    report_id: str,
    sha256: str,
    report_type: str,
    course_id: int,
    filename: str,
    generated_at: datetime,
) -> str:
    material = "|".join(
        [
            report_id,
            sha256,
            report_type,
            str(course_id),
            filename,
            generated_at.replace(microsecond=0).isoformat(),
        ]
    )
    return hmac.new(_key(), material.encode("utf-8"), hashlib.sha256).hexdigest()


def record_report(
    db: Session,
    *,
    report_id: str,
    course_id: int,
    report_type: str,
    file_format: str,
    filename: str,
    data: bytes,
    generated_by: int | None,
) -> ReportExport:
    generated_at = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    digest = checksum(data)
    row = ReportExport(
        report_id=report_id,
        course_id=course_id,
        report_type=report_type,
        format=file_format,
        filename=filename,
        sha256=digest,
        signature=_signature(
            report_id=report_id,
            sha256=digest,
            report_type=report_type,
            course_id=course_id,
            filename=filename,
            generated_at=generated_at,
        ),
        generated_by=generated_by,
        generated_at=generated_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def verify_report(db: Session, report_id: str, data: bytes) -> dict:
    row = db.query(ReportExport).filter(ReportExport.report_id == report_id).first()
    if row is None:
        return {"valid": False, "reason": "not_found"}

    expected = _signature(
        report_id=row.report_id,
        sha256=row.sha256,
        report_type=row.report_type,
        course_id=row.course_id,
        filename=row.filename,
        generated_at=row.generated_at,
    )
    if not hmac.compare_digest(expected, row.signature):
        return {"valid": False, "reason": "manifest_signature_invalid"}

    if not hmac.compare_digest(checksum(data), row.sha256):
        return {"valid": False, "reason": "checksum_mismatch"}

    course = db.query(Course).filter(Course.id == row.course_id).first()
    generator = (
        db.query(User).filter(User.id == row.generated_by).first()
        if row.generated_by
        else None
    )
    return {
        "valid": True,
        "report_id": row.report_id,
        "report_type": row.report_type,
        "format": row.format,
        "filename": row.filename,
        "course_code": course.code if course else None,
        "course_name": course.name if course else None,
        "generated_at": row.generated_at.isoformat() if row.generated_at else None,
        "generated_by_role": generator.role if generator else None,
        "sha256": row.sha256,
    }
