"""Event participation, placement, and trophy-challenge certificates.

The event logo and sponsors are already stored on ``Competition`` and
``CompetitionSponsor``. This module turns those records plus the event
achievement badges into a deterministic certificate that reuses the existing
public-verification path.
"""
from __future__ import annotations

import base64
import hashlib
import io
import logging
import re
import tempfile
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Achievement, Competition, CompetitionParticipant, User
from app.services import settings_service
from app.services.achievements import competition_achievement_parts
from app.services.pdf_report import _sanitize_for_pdf

logger = logging.getLogger(__name__)


def _pdf_text(value: object) -> str:
    """Return text the built-in PDF fonts can encode.

    Event names, recipient names, and dates are user-entered and may contain
    typographic dashes or accented characters that Helvetica/Times cannot
    encode. The certificate renderer must degrade to ASCII rather than fail.
    """
    return _sanitize_for_pdf(str(value or ""))

# Award keys are stable API values. Codes are compact, ASCII-safe parts of the
# certificate ID. Placement and trophy awards require the matching event badge.
AWARDS = {
    "participation": {
        "code": "p",
        "label": "Participation",
        "title": "Certificate of Participation",
        "role": "Participant",
        "achievement": None,
        "description": "Participated in the event.",
        "body": "has participated in",
    },
    "first": {
        "code": "1",
        "label": "1st Place",
        "title": "Certificate of Achievement",
        "role": "First place",
        "achievement": "ch",
        "description": "Finished first in the event.",
        "body": "has been awarded 1st Place in",
    },
    "second": {
        "code": "2",
        "label": "2nd Place",
        "title": "Certificate of Achievement",
        "role": "Second place",
        "achievement": "ru",
        "description": "Finished second in the event.",
        "body": "has been awarded 2nd Place in",
    },
    "third": {
        "code": "3",
        "label": "3rd Place",
        "title": "Certificate of Achievement",
        "role": "Third place",
        "achievement": "tp",
        "description": "Finished third in the event.",
        "body": "has been awarded 3rd Place in",
    },
    "first_blood": {
        "code": "fb",
        "label": "First Blood",
        "title": "Trophy Challenge Certificate",
        "role": "First Blood",
        "achievement": "fb",
        "description": "First participant to solve an exercise in the event.",
        "body": "has earned the First Blood trophy challenge in",
    },
    "clean_sweep": {
        "code": "cs",
        "label": "Clean Sweep",
        "title": "Trophy Challenge Certificate",
        "role": "Clean Sweep",
        "achievement": "cs",
        "description": "Solved every exercise in the event.",
        "body": "has earned the Clean Sweep trophy challenge in",
    },
    "perfect": {
        "code": "pr",
        "label": "Perfect Event",
        "title": "Trophy Challenge Certificate",
        "role": "Perfect Event",
        "achievement": "pr",
        "description": "Solved every event exercise without hints and on the first attempt.",
        "body": "has earned the Perfect Event trophy challenge in",
    },
    "discovery": {
        "code": "dv",
        "label": "Cyber Discovery",
        "title": "Cyber Discovery Experience Certificate",
        "role": "Cyber Discovery Participant",
        "achievement": None,
        "description": "Completed the Cyber Discovery Experience.",
        "body": "has completed the Cyber Discovery Experience",
        "serial_prefix": "DVF-CYBER-2027",
    },
}

AWARD_ORDER = (
    "participation",
    "discovery",
    "first",
    "second",
    "third",
    "first_blood",
    "clean_sweep",
    "perfect",
)
CODE_TO_AWARD = {award["code"]: key for key, award in AWARDS.items()}
ACHIEVEMENT_TO_AWARD = {
    award["achievement"]: key
    for key, award in AWARDS.items()
    if award["achievement"]
}
EVENT_CERTIFICATE_RE = re.compile(
    r"^OCR-EVT-(\d+)-(\d+)-([A-Z0-9]+)-([A-F0-9]{10})$"
)
SPONSOR_TIER_ORDER = {"gold": 0, "silver": 1, "bronze": 2}


def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def event_ended(competition: Competition, now: Optional[datetime] = None) -> bool:
    end = _as_utc(competition.end_at)
    if end is None:
        return False
    return (now or datetime.now(timezone.utc)) >= end


def certificate_base_url(db: Session, request_base_url: str = "") -> str:
    configured = (
        settings_service.get_setting(db, "certificate_verify_url", "") or ""
    ).rstrip("/")
    if configured:
        return configured
    if request_base_url:
        return request_base_url.rstrip("/")
    public_host = (getattr(settings, "SERVER_PUBLIC_HOST", "") or "").strip()
    if public_host:
        if not public_host.startswith(("http://", "https://")):
            public_host = f"https://{public_host}"
        return public_host.rstrip("/")
    return ""


def event_award_keys_for_user(
    db: Session, user_id: int, competition_id: int, experience_key: str | None = None
) -> list[str]:
    """Return the awards a participant has actually earned."""
    keys = {"participation"}
    if experience_key:
        # The Cyber Discovery certificate is event-scoped and available to
        # every participant after the event, like participation.
        keys.add("discovery")
    rows = (
        db.query(Achievement.achievement_type)
        .filter(
            Achievement.user_id == user_id,
            Achievement.achievement_type.like(f"comp_{competition_id}_%"),
        )
        .all()
    )
    for (achievement_type,) in rows:
        parts = competition_achievement_parts(achievement_type)
        if not parts:
            continue
        _competition_id, code = parts
        award_key = ACHIEVEMENT_TO_AWARD.get(code)
        if award_key:
            keys.add(award_key)
    return [key for key in AWARD_ORDER if key in keys]


def event_certificate_id(
    competition_id: int, user_id: int, award_key: str
) -> str:
    award = AWARDS[award_key]
    digest = hashlib.sha256(
        f"{user_id}:event:{competition_id}:{award_key}".encode()
    ).hexdigest()[:10].upper()
    return f"OCR-EVT-{competition_id}-{user_id}-{award['code']}-{digest}"


def parse_event_certificate_id(
    certificate_id: str,
) -> Optional[tuple[int, int, str, str]]:
    match = EVENT_CERTIFICATE_RE.match(str(certificate_id or "").strip().upper())
    if not match:
        return None
    competition_id, user_id, code, digest = match.groups()
    award_key = CODE_TO_AWARD.get(code.lower())
    if not award_key:
        return None
    return int(competition_id), int(user_id), award_key, digest


def event_certificate_serial(
    competition_id: int, user_id: int, award_key: str
) -> Optional[str]:
    award = AWARDS[award_key]
    prefix = award.get("serial_prefix")
    if not prefix:
        return None
    digest = hashlib.sha256(
        f"{user_id}:event:{competition_id}:{award_key}:serial".encode()
    ).hexdigest()[:5].upper()
    return f"{prefix}-{digest}"


def _sponsor_payload(competition: Competition) -> list[dict]:
    sponsors = sorted(
        competition.sponsors or [],
        key=lambda row: (
            SPONSOR_TIER_ORDER.get(getattr(row, "tier", "gold"), 9),
            getattr(row, "sort_order", 0) or 0,
            getattr(row, "name", ""),
        ),
    )
    return [
        {
            "name": sponsor.name,
            "logo_data": sponsor.logo_data,
            "tier": sponsor.tier or "gold",
        }
        for sponsor in sponsors
    ]


def _qr_data_uri(value: str) -> Optional[str]:
    try:
        import qrcode

        image = qrcode.make(value)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(
            buffer.getvalue()
        ).decode("ascii")
    except Exception as exc:  # pragma: no cover - QR is decorative
        logger.warning("Event certificate QR render failed: %s", exc)
        return None


def build_event_certificate(
    db: Session,
    user: User,
    competition: Competition,
    award_key: str,
    *,
    include_qr: bool = True,
    base_url: str = "",
) -> dict:
    if award_key not in AWARDS:
        raise ValueError(f"Unknown event award: {award_key}")
    award = AWARDS[award_key]
    certificate_id = event_certificate_id(competition.id, user.id, award_key)
    public_verification = bool(getattr(user, "certificates_public", True))
    base = certificate_base_url(db, base_url)
    verify_path = f"/verify/certificate/{certificate_id}"
    verify_url = f"{base}{verify_path}" if base else verify_path
    if not public_verification:
        verify_url = None
    qr_code = None
    if include_qr and public_verification:
        qr_code = _qr_data_uri(
            verify_url if verify_url and verify_url.startswith("http")
            else f"http://localhost{verify_path}"
        )

    start = _as_utc(competition.start_at)
    end = _as_utc(competition.end_at)
    if start and end:
        event_dates = (
            f"{start:%d %B %Y}"
            if start.date() == end.date()
            else f"{start:%d %B %Y} – {end:%d %B %Y}"
        )
    else:
        event_dates = ""
    issued = end or datetime.now(timezone.utc)

    return {
        "kind": "event",
        "certificate_id": certificate_id,
        "certificate_serial": event_certificate_serial(
            competition.id, user.id, award_key
        ),
        "award": award_key,
        "award_label": award["label"],
        "award_description": award["description"],
        "title": award["title"],
        "role_label": award["role"],
        "body_line": award["body"],
        "recipient": user.display_name,
        "competition_id": competition.id,
        "event_name": competition.name,
        "event_start": start.isoformat() if start else None,
        "event_end": end.isoformat() if end else None,
        "event_dates": event_dates,
        "event_logo": competition.logo_data,
        "sponsors": _sponsor_payload(competition),
        "issued_on": issued.date().isoformat(),
        "issued_display": issued.strftime("%d %B %Y"),
        "issuer": "SWOCTS",
        "public_verification": public_verification,
        "verify_url": verify_url,
        "qr_code": qr_code,
    }


def available_event_certificates(
    db: Session,
    user: User,
    competition: Competition,
    *,
    base_url: str = "",
) -> list[dict]:
    rows = []
    for award_key in event_award_keys_for_user(
        db, user.id, competition.id, competition.experience_key
    ):
        award = AWARDS[award_key]
        rows.append(
            {
                "award": award_key,
                "label": award["label"],
                "title": award["title"],
                "url": f"/certificate/event/{competition.id}/{award_key}",
                "pdf_url": (
                    f"/competitions/{competition.id}/certificate/"
                    f"{award_key}?format=pdf"
                ),
            }
        )
    return rows


def verify_event_certificate(
    db: Session, certificate_id: str, *, base_url: str = ""
) -> dict:
    invalid = {
        "valid": False,
        "certificate_id": certificate_id,
        "reason": "Certificate not found or no longer valid.",
    }
    parsed = parse_event_certificate_id(certificate_id)
    if not parsed:
        return invalid
    competition_id, user_id, award_key, digest = parsed
    competition = (
        db.query(Competition)
        .filter(Competition.id == competition_id)
        .first()
    )
    participant = (
        db.query(CompetitionParticipant)
        .filter(
            CompetitionParticipant.competition_id == competition_id,
            CompetitionParticipant.user_id == user_id,
        )
        .first()
    )
    user = db.query(User).filter(User.id == user_id).first()
    if not competition or not participant or not user:
        return invalid
    if not user.is_active or not user.is_approved:
        return invalid
    if not event_ended(competition):
        return invalid
    if not bool(getattr(user, "certificates_public", True)):
        return invalid
    if award_key not in event_award_keys_for_user(
        db, user_id, competition_id, competition.experience_key
    ):
        return invalid
    certificate = build_event_certificate(
        db, user, competition, award_key, include_qr=False, base_url=base_url
    )
    if certificate["certificate_id"] != certificate_id:
        return invalid
    return {
        "valid": True,
        "kind": "event",
        "certificate_id": certificate["certificate_id"],
        "recipient": certificate["recipient"],
        "event_name": certificate["event_name"],
        "event_start": certificate["event_start"],
        "event_end": certificate["event_end"],
        "event_dates": certificate["event_dates"],
        "award": certificate["award"],
        "award_label": certificate["award_label"],
        "award_description": certificate["award_description"],
        "issued_on": certificate["issued_on"],
        "issued_display": certificate["issued_display"],
        "issuer": certificate["issuer"],
        "message": "Certificate is valid and matches the event record.",
    }


# --- PDF -----------------------------------------------------------------

def _image_file(data_url: Optional[str]):
    """Return (temp path, width, height, temp handle) for a data-URL image."""
    if not data_url or "," not in data_url:
        return None
    try:
        from PIL import Image

        raw = base64.b64decode(data_url.split(",", 1)[1])
        image = Image.open(io.BytesIO(raw))
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        else:
            image = image.convert("RGB")
        handle = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(handle.name, format="PNG")
        handle.close()
        return handle.name, image.width, image.height, handle
    except Exception as exc:  # pragma: no cover - logo rendering is decorative
        logger.warning("Event certificate image render failed: %s", exc)
        return None


def _fit_image(pdf, path: str, width: int, height: int, max_w: float, max_h: float, x: float, y: float):
    if not width or not height:
        return
    scale = min(max_w / width, max_h / height)
    draw_w, draw_h = width * scale, height * scale
    pdf.image(path, x=x + (max_w - draw_w) / 2, y=y + (max_h - draw_h) / 2,
              w=draw_w, h=draw_h)


def event_certificate_pdf_bytes(certificate: dict) -> bytes:
    import os

    from fpdf import FPDF

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_title("SWOCTS Cyber Range event certificate")
    pdf.set_author("SWOCTS Cyber Range")
    pdf.set_subject(certificate.get("title") or "Event certificate")
    pdf.set_creator("SWOCTS Cyber Range")
    pdf.set_keywords("SWOCTS, cyber range, event, certificate")
    if hasattr(pdf, "set_lang"):
        pdf.set_lang("en")
    pdf.add_page()
    pdf.set_auto_page_break(False)

    gold = (176, 141, 60)
    ink = (31, 41, 55)
    muted = (107, 114, 128)
    paper = (255, 253, 248)
    pdf.set_fill_color(*paper)
    pdf.rect(0, 0, 297, 210, style="F")
    pdf.set_draw_color(*gold)
    pdf.set_line_width(1.2)
    pdf.rect(8, 8, 281, 194)
    pdf.set_line_width(0.3)
    pdf.set_draw_color(216, 192, 138)
    pdf.rect(12, 12, 273, 186)

    image_handles = []
    logo = _image_file(certificate.get("event_logo"))
    header_y = 18
    if logo:
        path, width, height, handle = logo
        image_handles.append(handle)
        _fit_image(pdf, path, width, height, 48, 22, 124.5, 16)
        header_y = 42

    pdf.set_text_color(*gold)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(0, header_y)
    pdf.cell(297, 5, "SWOCTS CYBER RANGE", align="C")

    pdf.set_text_color(*ink)
    pdf.set_font("Times", "B", 24)
    pdf.set_xy(0, header_y + 7)
    pdf.cell(297, 11, _pdf_text(certificate.get("title")) or "Event Certificate", align="C")

    pdf.set_draw_color(*gold)
    pdf.set_line_width(0.6)
    pdf.line(110, header_y + 20, 187, header_y + 20)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*muted)
    pdf.set_xy(0, header_y + 26)
    pdf.cell(297, 6, "This is to certify that", align="C")

    pdf.set_font("Times", "B", 27)
    pdf.set_text_color(17, 24, 39)
    pdf.set_xy(0, header_y + 33)
    pdf.cell(297, 13, _pdf_text(certificate.get("recipient")) or "Learner", align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*muted)
    pdf.set_xy(0, header_y + 49)
    pdf.cell(297, 6, _pdf_text(certificate.get("body_line")), align="C")

    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(*ink)
    pdf.set_xy(20, header_y + 56)
    pdf.multi_cell(257, 7, _pdf_text(certificate.get("event_name")), align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*muted)
    pdf.set_xy(0, header_y + 72)
    pdf.cell(297, 5, _pdf_text(certificate.get("event_dates")), align="C")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*gold)
    pdf.set_xy(20, header_y + 79)
    pdf.multi_cell(257, 4, _pdf_text(certificate.get("award_description")), align="C")

    sponsors = certificate.get("sponsors") or []
    if sponsors:
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*muted)
        pdf.set_xy(0, 151)
        pdf.cell(297, 4, "SUPPORTED BY", align="C")
        visible = sponsors[:6]
        cell_w = 257 / max(len(visible), 1)
        for index, sponsor in enumerate(visible):
            x = 20 + index * cell_w
            image = _image_file(sponsor.get("logo_data"))
            if image:
                path, width, height, handle = image
                image_handles.append(handle)
                _fit_image(pdf, path, width, height, cell_w - 6, 11, x + 3, 156)
            pdf.set_font("Helvetica", "", 6.5)
            pdf.set_text_color(*ink)
            pdf.set_xy(x, 168)
            pdf.cell(cell_w, 4, _pdf_text(sponsor.get("name"))[:32], align="C")

    pdf.set_draw_color(216, 192, 138)
    pdf.set_line_width(0.4)
    pdf.line(20, 176, 277, 176)

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*muted)
    pdf.set_xy(24, 181)
    pdf.cell(50, 4, "DATE AWARDED")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*ink)
    pdf.set_xy(24, 186)
    pdf.cell(60, 4, _pdf_text(certificate.get("issued_display")))

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*muted)
    pdf.set_xy(95, 181)
    pdf.cell(80, 4, "CERTIFICATE ID")
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(*ink)
    pdf.set_xy(95, 186)
    pdf.cell(120, 4, _pdf_text(certificate.get("certificate_id")))

    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*muted)
    pdf.set_xy(24, 192)
    pdf.cell(60, 3, "VERIFY" if certificate.get("public_verification", True) else "PUBLIC VERIFICATION")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*gold)
    pdf.set_xy(24, 195)
    pdf.cell(210, 4, _pdf_text(certificate.get("verify_url")) or "Off by account holder")

    qr_code = certificate.get("qr_code")
    if qr_code:
        try:
            encoded = qr_code.split(",", 1)[1] if "," in qr_code else qr_code
            handle = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            handle.write(base64.b64decode(encoded))
            handle.close()
            image_handles.append(handle)
            pdf.image(handle.name, x=252, y=180, w=20)
        except Exception as exc:  # pragma: no cover
            logger.warning("Event certificate QR render failed: %s", exc)

    try:
        return bytes(pdf.output())
    finally:
        for handle in image_handles:
            try:
                os.unlink(handle.name)
            except OSError:
                pass
