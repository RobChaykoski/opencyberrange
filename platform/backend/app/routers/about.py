"""Read-only About inventory: versions, licences, branding, and SBOM files.

The data is generated into ``app/data/about`` by ``scripts/generate-about.py``.
Access is limited to signed-in users; it contains no secrets, but it is not a
public endpoint.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth import get_current_user
from app.models import User
from app.version import APP_VERSION, RELEASE_NAME

router = APIRouter()

ABOUT_DIR = Path(__file__).resolve().parent.parent / "data" / "about"
LICENCES_DIR = ABOUT_DIR / "licenses"
SBOM_DIR = ABOUT_DIR / "sbom"


def _safe_file(directory: Path, name: str) -> Path:
    """Resolve a file inside *directory*, rejecting traversal and missing files."""
    if not name or Path(name).name != name:
        raise HTTPException(status_code=404, detail="Not found")
    path = (directory / name).resolve()
    if directory.resolve() not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return path


@router.get("")
async def get_about(_user: User = Depends(get_current_user)):
    """Return the generated component, licence, branding, and SBOM inventory."""
    path = ABOUT_DIR / "about.json"
    if not path.is_file():
        raise HTTPException(status_code=503, detail="About inventory is not available")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = APP_VERSION
    data["release"] = RELEASE_NAME
    return data


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
