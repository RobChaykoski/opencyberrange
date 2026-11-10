"""Read-only About inventory: live build/runtime state plus release artefacts.

The static inventory is generated into ``app/data/about`` by
``scripts/generate-about.py``. Build identity and runtime values are resolved
from the running container and database so the page does not go stale when a
new release is deployed. Access is limited to signed-in users; it contains no
secrets, but it is not a public endpoint.
"""

from __future__ import annotations

import json
import os
import platform as platform_module
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import engine, get_db
from app.models import User
from app.version import APP_VERSION, RELEASE_NAME

router = APIRouter()

ABOUT_DIR = Path(__file__).resolve().parent.parent / "data" / "about"
LICENCES_DIR = ABOUT_DIR / "licenses"
SBOM_DIR = ABOUT_DIR / "sbom"
BUILD_FILE = ABOUT_DIR / "build.json"


def _safe_file(directory: Path, name: str) -> Path:
    """Return an existing file in *directory* by exact name.

    The path comes from a directory listing, so a caller-supplied value is
    never used to construct a filesystem path. This keeps traversal attempts
    and symlink tricks out of the file-serving routes.
    """
    if not name:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        for entry in directory.iterdir():
            if entry.name == name and entry.is_file():
                return entry
    except OSError:
        pass
    raise HTTPException(status_code=404, detail="Not found")


def _read_build() -> dict:
    try:
        return json.loads(BUILD_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _database_runtime(db: Session) -> dict[str, str]:
    runtime: dict[str, str] = {}
    try:
        version = db.execute(text("SHOW server_version")).scalar()
        if version:
            runtime["postgres"] = str(version).split()[0]
    except Exception:
        pass
    try:
        revision = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
        runtime["schema_revision"] = str(revision or "unknown")
    except Exception:
        runtime["schema_revision"] = "unknown"
    return runtime


def _content_counts(db: Session) -> dict[str, int]:
    try:
        row = db.execute(
            text(
                "SELECT "
                "(SELECT COUNT(*) FROM labs) AS labs, "
                "(SELECT COUNT(*) FROM tracks) AS tracks, "
                "(SELECT COUNT(*) FROM levels) AS levels"
            )
        ).mappings().one()
        return {key: int(row[key] or 0) for key in ("labs", "tracks", "levels")}
    except Exception:
        return {}


def _integrity_summary() -> dict:
    try:
        from app.services.db_integrity import ledger_summary

        summary = ledger_summary(engine)
    except Exception:
        return {"status": "unavailable", "entries": 0, "unattributed_7d": 0}
    if not summary.get("available"):
        status = "unavailable"
    elif not summary.get("installed"):
        status = "error"
    elif int(summary.get("unattributed_7d") or 0):
        status = "warning"
    else:
        status = "ok"
    return {
        "status": status,
        "entries": int(summary.get("entries") or 0),
        "unattributed_7d": int(summary.get("unattributed_7d") or 0),
    }


def _image_digests() -> dict[str, str]:
    try:
        from app.services import docker_manager

        client = docker_manager.client
        if client is None:
            return {}
        names = {
            "backend": os.environ.get("OCR_BACKEND_CONTAINER", "ocr-backend"),
            "frontend": os.environ.get("OCR_FRONTEND_CONTAINER", "ocr-frontend"),
        }
        digests: dict[str, str] = {}
        for label, name in names.items():
            try:
                image_id = client.containers.get(name).image.id
                if image_id:
                    digests[label] = image_id
            except Exception:
                continue
        return digests
    except Exception:
        return {}


def _live_overlay(data: dict, db: Session) -> dict:
    build = _read_build()
    platform_data = data.setdefault("platform", {})
    runtime = {
        "python": platform_module.python_version(),
        "node": str(build.get("node") or platform_data.get("node") or ""),
        "redis": str(build.get("redis") or platform_data.get("redis") or ""),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    runtime.update(_database_runtime(db))
    try:
        from app import entitlement

        runtime["edition"] = entitlement.edition_name()
    except Exception:
        runtime["edition"] = str(
            build.get("edition") or platform_data.get("edition") or ""
        )

    platform_data.update(
        {
            "version": APP_VERSION,
            "status": build.get("status") or platform_data.get("status", "release"),
            "edition": runtime["edition"],
            "python": runtime["python"],
            "node": runtime["node"],
            "postgres": runtime.get("postgres") or platform_data.get("postgres", ""),
            "redis": runtime["redis"],
        }
    )

    env_revision = os.environ.get("OCR_BUILD_REVISION", "").strip()
    if not env_revision or env_revision.lower() == "unknown":
        env_revision = build.get("git_sha", "unknown")

    data.update(
        {
            "version": APP_VERSION,
            "release": RELEASE_NAME,
            "generated_for_release": build.get("version") or APP_VERSION,
            "release_date": build.get("release_date") or data.get("release_date"),
            "build": {
                "version": APP_VERSION,
                "git_sha": env_revision,
                "built_at": build.get("built_at"),
                "release_date": build.get("release_date"),
                "image_digests": _image_digests(),
            },
            "runtime": runtime,
            "content": _content_counts(db),
            "integrity": _integrity_summary(),
        }
    )
    return data


@router.get("")
async def get_about(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Return the release inventory with live build and runtime values."""
    path = ABOUT_DIR / "about.json"
    if not path.is_file():
        raise HTTPException(status_code=503, detail="About inventory is not available")
    data = json.loads(path.read_text(encoding="utf-8"))
    return _live_overlay(data, db)


@router.get("/licences/{name}")
async def get_licence(name: str, _user: User = Depends(get_current_user)):
    """Serve a project or third-party licence document."""
    path = _safe_file(LICENCES_DIR, name)
    return FileResponse(
        path,
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "private, max-age=300"},
    )


@router.get("/sbom/{name}")
async def get_sbom(name: str, _user: User = Depends(get_current_user)):
    """Serve a generated CycloneDX SBOM as a download."""
    path = _safe_file(SBOM_DIR, name)
    return FileResponse(
        path,
        media_type="application/json",
        filename=name,
        headers={"Cache-Control": "private, max-age=300"},
    )
