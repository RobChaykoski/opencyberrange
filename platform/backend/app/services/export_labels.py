"""Data-classification metadata shared by every export path.

The admin chooses a classification, organisation, and optional handling note
under Settings -> Data labels. Exports carry the label in their document
metadata and in response headers; JSON exports also get an export_metadata
object. The setting is intentionally central so a new export does not have to
re-invent a labelling scheme.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.services import settings_service

CLASSIFICATION_LABELS = {
    "public": "Public",
    "internal": "Internal",
    "confidential": "Confidential",
    "restricted": "Restricted",
}

DEFAULT_HANDLING = {
    "public": "Approved for public release.",
    "internal": "Internal use. Share only within the institution.",
    "confidential": "Confidential. Share only with authorised recipients.",
    "restricted": "Restricted. Handle under the institution's data policy.",
}


def _setting(db, key: str, default: str = "") -> str:
    return (settings_service.get_setting_fresh(db, key, default) or default).strip()


def export_labels() -> dict[str, Any] | None:
    """Return the configured export metadata, or None when labels are off."""
    try:
        db = SessionLocal()
    except Exception:
        # A label is advisory metadata; never fail an export because the
        # settings read is unavailable.
        return None
    try:
        try:
            if _setting(db, "export_label_enabled", "true").lower() not in {
                "true",
                "1",
                "yes",
                "on",
            }:
                return None
            classification = _setting(db, "export_classification", "internal").lower()
            if classification not in CLASSIFICATION_LABELS:
                classification = "internal"
            organisation = _setting(db, "export_organisation") or "SWOCTS Cyber Range"
            handling = _setting(db, "export_handling_note") or DEFAULT_HANDLING[classification]
            include_timestamp = _setting(
                db, "export_include_timestamp", "true"
            ).lower() in {"true", "1", "yes", "on"}
        except Exception:
            return None
        result: dict[str, Any] = {
            "classification": CLASSIFICATION_LABELS[classification],
            "classification_key": classification,
            "organisation": organisation,
            "handling": handling,
            "source": "OpenCyberRange",
        }
        if include_timestamp:
            result["generated_at"] = datetime.now(timezone.utc).replace(
                microsecond=0
            ).isoformat()
        return result
    finally:
        db.close()


def _pdf_text(value: str) -> str:
    """Keep PyFPDF's core fonts from choking on admin-supplied Unicode."""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("latin-1", "replace").decode("latin-1")


def apply_pdf_metadata(pdf, title: str, subject: str) -> None:
    """Stamp PDF document properties with the configured label.

    Called after a document object exists, before/alongside its normal title
    metadata. When labels are disabled this is a no-op so the report keeps its
    historical metadata.
    """
    labels = export_labels()
    if not labels:
        return
    keyword_parts = [
        "OpenCyberRange",
        labels["classification"],
        subject,
    ]
    if labels.get("handling"):
        keyword_parts.append(labels["handling"])
    if labels.get("generated_at"):
        keyword_parts.append(labels["generated_at"])
    pdf.set_title(_pdf_text(title))
    pdf.set_author(_pdf_text(labels["organisation"]))
    pdf.set_subject(_pdf_text(f"{subject} - {labels['classification']}"))
    pdf.set_creator("OpenCyberRange")
    pdf.set_keywords(_pdf_text(", ".join(keyword_parts)))


def export_response_headers() -> dict[str, str]:
    """Headers added by the export-label middleware."""
    labels = export_labels()
    if not labels:
        return {}
    headers = {
        "X-Data-Classification": labels["classification"],
        "X-Data-Organisation": labels["organisation"],
        "X-Data-Handling": labels["handling"],
        "X-Data-Source": labels["source"],
    }
    if labels.get("generated_at"):
        headers["X-Export-Generated-At"] = labels["generated_at"]
    return headers


def export_metadata() -> dict[str, Any]:
    """JSON-friendly metadata for application/json exports."""
    labels = export_labels()
    return dict(labels) if labels else {}
