"""Data-classification metadata shared by every export path.

The admin chooses a classification, organisation, and optional handling note
under Settings -> Data labels. Exports carry the label in their document
metadata and in response headers; JSON exports also get an export_metadata
object. The setting is intentionally central so a new export does not have to
re-invent a labelling scheme.
"""

from __future__ import annotations

import html
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.services import settings_service

logger = logging.getLogger(__name__)

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

BUILTIN_LEVELS: dict[str, dict[str, Any]] = {
    "public": {
        "key": "public",
        "label": "Public",
        "rank": 0,
        "handling": DEFAULT_HANDLING["public"],
        "exportable": True,
    },
    "internal": {
        "key": "internal",
        "label": "Internal",
        "rank": 1,
        "handling": DEFAULT_HANDLING["internal"],
        "exportable": True,
    },
    "confidential": {
        "key": "confidential",
        "label": "Confidential",
        "rank": 2,
        "handling": DEFAULT_HANDLING["confidential"],
        "exportable": True,
    },
    "restricted": {
        "key": "restricted",
        "label": "Restricted",
        "rank": 3,
        "handling": DEFAULT_HANDLING["restricted"],
        "exportable": True,
    },
}

# What a download contains, independent of the configured default label. The
# effective label is the higher-ranked of this path classification and the
# admin default, so an institution can raise (but not accidentally lower) it.
EXPORT_CLASSIFICATION_PREFIXES: tuple[tuple[str, str], ...] = (
    ("/api/admin/system/backups", "restricted"),
    ("/api/admin/users/export", "restricted"),
    ("/api/admin/activity/export", "confidential"),
    ("/api/admin/reports", "confidential"),
    ("/api/admin/labs", "confidential"),
    ("/api/instructor/labs", "confidential"),
    ("/api/instructor", "confidential"),
    ("/api/auth/export", "confidential"),
    ("/api/profile/portfolio", "confidential"),
    ("/api/profile/career-dossier", "confidential"),
    ("/api/profile/snapshots", "confidential"),
    ("/api/profile/transcript", "confidential"),
    ("/api/reports", "confidential"),
    ("/api/analytics", "confidential"),
    ("/api/dashboard", "confidential"),
    ("/api/courses", "confidential"),
    ("/api/exercise-tester", "confidential"),
    ("/api/badges", "public"),
    ("/api/exercises/verify/certificate", "public"),
    ("/api/version", "public"),
)

_LEVEL_KEY = re.compile(r"^[a-z][a-z0-9_]{0,31}$")


def _setting(db, key: str, default: str = "") -> str:
    return (settings_service.get_setting_fresh(db, key, default) or default).strip()


def classification_for_path(path: str | None) -> str | None:
    """Return the minimum classification implied by an export path."""
    normalized = path or ""
    for prefix, key in EXPORT_CLASSIFICATION_PREFIXES:
        if (
            normalized == prefix
            or normalized.startswith(prefix + "/")
            or normalized.startswith(prefix + ".")
        ):
            return key
    return None


def _custom_levels(raw: str) -> tuple[dict[str, dict[str, Any]] | None, list[str]]:
    """Parse an institution-defined level list, with actionable warnings."""
    if not raw:
        return None, []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"Custom levels are not valid JSON: {exc}"]
    if not isinstance(payload, list) or len(payload) < 2:
        return None, ["Custom levels must be a list with at least two levels."]
    levels: dict[str, dict[str, Any]] = {}
    ranks = set()
    warnings: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            return None, ["Each custom level must be an object."]
        key = str(item.get("key") or "").strip().lower()
        label = str(item.get("label") or "").strip()
        try:
            rank = int(item.get("rank"))
        except (TypeError, ValueError):
            return None, [f"Level '{key or '?'}' needs an integer rank."]
        if not _LEVEL_KEY.fullmatch(key):
            return None, [f"Invalid level key: {key!r}"]
        if not label:
            return None, [f"Level '{key}' needs a label."]
        if rank < 0 or rank > 100:
            return None, [f"Level '{key}' rank must be between 0 and 100."]
        if rank in ranks:
            return None, [f"Level '{key}' reuses rank {rank}."]
        ranks.add(rank)
        levels[key] = {
            "key": key,
            "label": label[:64],
            "rank": rank,
            "handling": str(item.get("handling") or "").strip()
            or "Handle under the institution's data policy.",
            "exportable": bool(item.get("exportable", True)),
        }
    return levels, warnings


def load_levels(db) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Return the effective level map and any custom-scheme warnings."""
    custom, warnings = _custom_levels(_setting(db, "data_label_custom_levels"))
    if custom:
        return custom, warnings
    return dict(BUILTIN_LEVELS), warnings


def _level_for_key(levels: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    return levels.get(key) or levels.get("internal") or next(iter(levels.values()))


def _effective_level(
    levels: dict[str, dict[str, Any]], configured: str, forced: str | None
) -> dict[str, Any]:
    configured_level = _level_for_key(levels, configured)
    if not forced:
        return configured_level
    forced_level = _level_for_key(levels, forced)
    return forced_level if forced_level["rank"] >= configured_level["rank"] else configured_level


def export_labels(classification: str | None = None) -> dict[str, Any] | None:
    """Return configured export metadata, or None when labels are off."""
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
            levels, _warnings = load_levels(db)
            configured = _setting(db, "export_classification", "internal").lower()
            level = _effective_level(levels, configured, classification)
            organisation = _setting(db, "export_organisation") or "SWOCTS Cyber Range"
            handling = (
                _setting(db, "export_handling_note") or level["handling"]
            )
            include_timestamp = _setting(
                db, "export_include_timestamp", "true"
            ).lower() in {"true", "1", "yes", "on"}
        except Exception:
            return None
        result: dict[str, Any] = {
            "classification": level["label"],
            "classification_key": level["key"],
            "classification_rank": level["rank"],
            "organisation": organisation,
            "handling": handling,
            "source": "OpenCyberRange",
        }
        region = _setting(db, "data_label_region")
        if region:
            result["region"] = region
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


def export_response_headers(path: str | None = None) -> dict[str, str]:
    """Headers added by the export-label middleware."""
    labels = export_labels(classification_for_path(path))
    if not labels:
        return {}
    headers = {
        "X-Data-Classification": labels["classification"],
        "X-Data-Classification-Key": labels["classification_key"],
        "X-Data-Organisation": labels["organisation"],
        "X-Data-Handling": labels["handling"],
        "X-Data-Source": labels["source"],
    }
    if labels.get("region"):
        headers["X-Data-Region"] = labels["region"]
    if labels.get("generated_at"):
        headers["X-Export-Generated-At"] = labels["generated_at"]
    return headers


def export_metadata() -> dict[str, Any]:
    """JSON-friendly metadata for application/json exports."""
    labels = export_labels()
    return dict(labels) if labels else {}


def _label_lines(labels: dict[str, Any]) -> list[str]:
    lines = [f"Data classification: {labels['classification']}"]
    lines.append(f"Organisation: {labels['organisation']}")
    if labels.get("handling"):
        lines.append(f"Handling: {labels['handling']}")
    if labels.get("generated_at"):
        lines.append(f"Generated: {labels['generated_at']}")
    return lines


def csv_with_labels(data: bytes) -> bytes:
    """Prepend human-readable label comments to a CSV download.

    The comment rows are intentionally marked with ``#`` so a reader can see
    the handling instruction before the header row. The response headers still
    carry the machine-readable version.
    """
    labels = export_labels()
    if not labels:
        return data
    text = data.decode("utf-8-sig")
    prefix = "".join(f"# {line}\n" for line in _label_lines(labels))
    return ("\ufeff" + prefix + text).encode("utf-8")


def markdown_with_labels(text: str) -> str:
    labels = export_labels()
    if not labels:
        return text
    lines = _label_lines(labels)
    block = "\n".join(f"> **{line.split(': ', 1)[0]}:** {line.split(': ', 1)[1]}" for line in lines)
    return f"{block}\n\n---\n\n{text}"


def html_with_labels(content: str) -> str:
    labels = export_labels()
    if not labels:
        return content
    lines = "".join(
        f"<div><strong>{html.escape(line.split(': ', 1)[0])}:</strong> "
        f"{html.escape(line.split(': ', 1)[1])}</div>"
        for line in _label_lines(labels)
    )
    banner = (
        '<div style="margin:0 0 1rem;padding:0.75rem 1rem;border:1px solid #cbd5e1;'
        'border-left:4px solid #2563eb;border-radius:6px;background:#f8fafc;'
        'color:#334155;font:13px/1.45 system-ui,sans-serif">'
        f"{lines}</div>"
    )
    marker = "<body"
    index = content.lower().find(marker)
    if index == -1:
        return banner + content
    close = content.find(">", index)
    if close == -1:
        return banner + content
    return content[: close + 1] + banner + content[close + 1 :]

