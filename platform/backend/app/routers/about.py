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

from fastapi import APIRouter, Depends, HTTPException, Response
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


def _safe_scalar(db: Session, sql: str):
    try:
        with db.begin_nested():
            return db.execute(text(sql)).scalar()
    except Exception:
        return None


def _database_runtime(db: Session) -> dict[str, str]:
    runtime: dict[str, str] = {}
    version = _safe_scalar(db, "SHOW server_version")
    if version:
        runtime["postgres"] = str(version).split()[0]
    if _safe_scalar(db, "SELECT to_regclass('public.alembic_version') IS NOT NULL"):
        revision = _safe_scalar(db, "SELECT version_num FROM alembic_version")
        runtime["schema_revision"] = str(revision or "unknown")
    else:
        runtime["schema_revision"] = "unknown"
    return runtime


def _content_counts(db: Session) -> dict[str, int]:
    try:
        with db.begin_nested():
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
    elif int(summary.get("unreviewed_7d") or 0):
        status = "warning"
    else:
        status = "ok"
    unattributed = int(summary.get("unattributed_7d") or 0)
    unreviewed_raw = summary.get("unreviewed_7d")
    unreviewed = int(
        unattributed if unreviewed_raw is None else unreviewed_raw
    )
    return {
        "status": status,
        "entries": int(summary.get("entries") or 0),
        "unattributed_7d": unattributed,
        "unreviewed_7d": unreviewed,
    }


def _image_digests() -> dict[str, str]:
    try:
        import docker

        client = docker.from_env()
        names = {
            "backend": os.environ.get("OCR_BACKEND_CONTAINER", "ocr-backend"),
            "frontend": os.environ.get("OCR_FRONTEND_CONTAINER", "ocr-frontend"),
        }
        digests: dict[str, str] = {}
        for label, name in names.items():
            try:
                container = client.containers.get(name)
                image_id = container.attrs.get("Image")
                if not image_id:
                    image_id = container.image.id
                if image_id:
                    digests[label] = image_id
            except Exception:
                continue
        return digests
    except Exception:
        return {}


def _edition_label(value: str) -> str:
    return {
        "lite": "Community / Academic",
        "community": "Community / Academic",
        "professional": "Professional",
        "enterprise": "Enterprise",
    }.get(str(value).lower(), str(value))


def _docker_runtime() -> dict:
    try:
        import docker

        client = docker.from_env()
        info = client.info()
        payload = {
            "docker": str(info.get("ServerVersion") or ""),
            "host_os": str(info.get("OperatingSystem") or ""),
            "kernel": str(info.get("KernelVersion") or ""),
            "host_cpu": info.get("NCPU"),
            "host_memory": info.get("MemTotal"),
        }
        client.close()
        return {key: value for key, value in payload.items() if value not in (None, "")}
    except Exception:
        return {}


def _host_health() -> dict:
    """Host package/reboot status written by scripts/collect-host-health.sh."""
    path = os.environ.get("HOST_HEALTH_FILE", "/app/backups/host-health.json")
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return {"available": False}
    if not isinstance(data, dict):
        return {"available": False}
    data["available"] = True
    return data


def _platform_health(runtime: dict, host_health: dict | None = None) -> list[dict]:
    """Current vs supported/target versions and the upgrade path for each."""
    components = [
        {
            "key": "platform",
            "name": "Platform release",
            "current": APP_VERSION,
            "target": "current supported line",
            "status": "current",
            "note": "Signed release; see the tag and changelog.",
            "path": "docs/RELEASES.md",
        },
        {
            "key": "host_os",
            "name": "Host OS",
            "current": runtime.get("host_os") or "unknown",
            "target": "Ubuntu 26.04 LTS candidate",
            "status": "upgrade-candidate",
            "note": "Certified on 24.04; 26.04 is the next LTS test candidate.",
            "path": "docs/UBUNTU-NEXT-UPGRADE-CANDIDATE.md",
        },
        {
            "key": "kernel",
            "name": "Kernel",
            "current": runtime.get("kernel") or "unknown",
            "target": "matches the host OS",
            "status": "current",
            "note": "Reported by the container runtime.",
            "path": "docs/UBUNTU-NEXT-UPGRADE-CANDIDATE.md",
        },
        {
            "key": "docker",
            "name": "Docker Engine",
            "current": runtime.get("docker") or "unknown",
            "target": "Engine 24+ with Compose v2",
            "status": "current",
            "note": "Single-host supported shape.",
            "path": "docs/DEPLOYMENT-RUNBOOK.md",
        },
        {
            "key": "python",
            "name": "Python runtime",
            "current": runtime.get("python") or "unknown",
            "target": "3.13 compatibility target",
            "status": "upgrade-planned",
            "note": "3.11 is the supported runtime; 3.13 is in compatibility testing.",
            "path": "versions.yaml",
        },
        {
            "key": "postgres",
            "name": "PostgreSQL",
            "current": runtime.get("postgres") or "unknown",
            "target": "17 major upgrade",
            "status": "upgrade-planned",
            "note": "Dump/restore migration is required; plan a maintenance window.",
            "path": "docs/DEPLOYMENT-RUNBOOK.md",
        },
        {
            "key": "node",
            "name": "Node build toolchain",
            "current": runtime.get("node") or "unknown",
            "target": "24 compatibility target",
            "status": "supported",
            "note": "Build-time only; not shipped in the frontend image.",
            "path": "versions.yaml",
        },
        {
            "key": "schema",
            "name": "Database schema",
            "current": runtime.get("schema_revision") or "unknown",
            "target": "Alembic head",
            "status": "current",
            "note": "Applied by the release deployment.",
            "path": "docs/DEPLOYMENT-RUNBOOK.md",
        },
    ]
    if host_health and host_health.get("available"):
        upgradable = int(host_health.get("upgradable_packages") or 0)
        security = int(host_health.get("security_updates") or 0)
        reboot = bool(host_health.get("reboot_required"))
        note = f"{upgradable} package(s) upgradable"
        if security:
            note += f", {security} security"
        if reboot:
            note += "; reboot required"
        components.append(
            {
                "key": "packages",
                "name": "OS packages",
                "current": f"{upgradable} upgradable",
                "target": "security updates applied in a maintenance window",
                "status": "upgrade-planned" if (upgradable or reboot) else "current",
                "note": note,
                "path": "docs/DEPLOYMENT-RUNBOOK.md",
            }
        )
    return components


def _live_overlay(data: dict, db: Session) -> dict:
    build = _read_build()
    platform_data = data.setdefault("platform", {})
    runtime = {
        "python": platform_module.python_version(),
        "node": str(build.get("node") or platform_data.get("node") or ""),
        "valkey": str(
            build.get("valkey")
            or platform_data.get("valkey")
            or build.get("redis")
            or platform_data.get("redis")
            or ""
        ),
        "redis": str(
            build.get("valkey")
            or platform_data.get("valkey")
            or build.get("redis")
            or platform_data.get("redis")
            or ""
        ),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    runtime.update(_database_runtime(db))
    runtime.update(_docker_runtime())
    try:
        from app import entitlement

        runtime["edition"] = _edition_label(entitlement.edition_name())
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
    host_health = _host_health()

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
            "platform_health": _platform_health(runtime, host_health),
            "host_updates": host_health,
            "upgrade": {
                "runbook": "docs/DEPLOYMENT-RUNBOOK.md",
                "readiness": "docs/RELEASE-5-PRODUCTION-READINESS.md",
                "backup": "bash scripts/backup-production.sh",
                "check": "bash scripts/monitor-deployment.sh",
                "upgrade_command": "git pull --ff-only && docker compose build backend frontend && docker compose up -d backend frontend && docker exec ocr-backend alembic -c alembic.ini upgrade head",
                "rollback": "Restore the pre-deploy dump and the retained previous image tags; see the readiness rollback section.",
            },
            "content": _content_counts(db),
            "integrity": _integrity_summary(),
        }
    )
    return data


@router.get("")
async def get_about(
    response: Response,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Return the release inventory with live build and runtime values."""
    path = ABOUT_DIR / "about.json"
    if not path.is_file():
        raise HTTPException(status_code=503, detail="About inventory is not available")
    data = json.loads(path.read_text(encoding="utf-8"))
    # This payload changes when the backend is upgraded. Do not let a browser
    # or intermediary keep an older release version after a deployment.
    response.headers["Cache-Control"] = "no-store"
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
