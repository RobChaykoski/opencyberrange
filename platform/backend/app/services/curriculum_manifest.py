"""Central curriculum manifest lookup.

The manifest is mounted read-only at /app/curriculum-manifest.yaml in the
container. Local tests fall back to the repository copy.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from app.config import settings


def _manifest_path() -> Path:
    configured = getattr(settings, "CURRICULUM_MANIFEST_PATH", None)
    if configured:
        return Path(configured)
    container = Path("/app/curriculum-manifest.yaml")
    if container.is_file():
        return container
    # platform/backend/app/services -> repository root
    try:
        return Path(__file__).resolve().parents[4] / "curriculum-manifest.yaml"
    except IndexError:
        return container


@lru_cache(maxsize=1)
def load_manifest() -> dict:
    path = _manifest_path()
    if not path.is_file():
        return {"tracks": []}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {"tracks": []}
    except Exception:
        return {"tracks": []}


@lru_cache(maxsize=1)
def _chapters() -> dict[str, dict]:
    chapters: dict[str, dict] = {}
    for track in load_manifest().get("tracks", []):
        for chapter in track.get("chapters", []):
            chapter_id = str(chapter.get("id") or "").strip()
            if chapter_id:
                entry = dict(chapter)
                entry["track_id"] = track.get("id")
                entry["track_name"] = track.get("display_name")
                chapters[chapter_id] = entry
    return chapters


@lru_cache(maxsize=1)
def _by_directory() -> dict[str, dict]:
    result = {}
    for chapter in _chapters().values():
        directory = str(chapter.get("directory") or "").strip()
        if directory:
            result[directory] = chapter
    return result


def chapter(chapter_id: Optional[str]) -> Optional[dict]:
    if not chapter_id:
        return None
    return _chapters().get(str(chapter_id))


def chapter_for_workbook(workbook: Optional[str]) -> Optional[dict]:
    """Return the chapter whose directory appears in a workbook path."""
    if not workbook:
        return None
    parts = Path(str(workbook).replace("\\", "/")).parts
    for part in parts:
        match = _by_directory().get(part)
        if match:
            return match
    return None


def chapter_id_for_workbook(workbook: Optional[str]) -> Optional[str]:
    match = chapter_for_workbook(workbook)
    return str(match.get("id")) if match else None


def chapter_name(chapter_id: Optional[str]) -> Optional[str]:
    match = chapter(chapter_id)
    return str(match.get("display_name")) if match else None


def chapter_label(chapter_id: Optional[str]) -> Optional[str]:
    match = chapter(chapter_id)
    if not match:
        return None
    return f"{match.get('id')}: {match.get('display_name')}"
