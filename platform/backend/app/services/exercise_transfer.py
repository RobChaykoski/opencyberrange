"""Exercise export/import for reuse across OpenCyberRange instances.

An export is a normal authoring ZIP (``lab.yaml`` + ``docker-compose.yml`` +
``containers/``) plus a small manifest and README. Imports run through the same
validator/extractor as an instructor upload and always create a **draft** lab so
a reused exercise is reviewed before students see it.

By default the exported ``lab.yaml`` has its flag replaced with a placeholder.
The importer generates a new flag (or accepts one) and writes it back, so two
copies of the same exercise never share a flag. A trusted admin can export with
the original flag for backup/restore.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import secrets
import shutil
import zipfile
from datetime import datetime, timezone

import yaml
from sqlalchemy.orm import Session

from app.models import Lab, Level, Track
from app.services import lab_upload
from app.services.curriculum_manifest import chapter_id_for_workbook
from app.services.docker_manager import get_track_directory_name
from app.services.framework_map import resolve as resolve_framework

FORMAT = "opencyberrange-exercise"
FORMAT_VERSION = 1
PLACEHOLDER_FLAG = "OCR{REPLACE_ME}"
MAX_EXPORT_BYTES = lab_upload.MAX_ZIP_SIZE
MAX_IMPORT_BYTES = 50 * 1024 * 1024
SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
}
SKIP_FILES = {"export-manifest.json", "EXPORT-README.md", ".DS_Store"}
SKIP_SUFFIXES = (".pyc", ".pyo")
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,149}$")
_PLATFORM_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
)


class ExerciseTransferError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _labs_roots() -> list[str]:
    candidates = [
        os.environ.get("LABS_DIR"),
        os.environ.get("OCR_LABS_ROOT"),
        getattr(lab_upload, "LABS_ROOT", None),
        "/labs",
        os.path.join(_PLATFORM_DIR, "labs"),
    ]
    roots = []
    for candidate in candidates:
        if candidate and os.path.isdir(candidate):
            real = os.path.realpath(candidate)
            if real not in roots:
                roots.append(real)
    return roots


def _labs_root() -> str:
    roots = _labs_roots()
    if not roots:
        return os.path.realpath(getattr(lab_upload, "LABS_ROOT", "/labs"))
    return roots[0]


def _safe_lab_dir(slug: str) -> str | None:
    if not slug or not _SLUG_RE.fullmatch(slug):
        return None
    for root in _labs_roots():
        for entry in os.scandir(root):
            if not entry.is_dir(follow_symlinks=False):
                continue
            candidate = os.path.join(entry.path, slug)
            if not os.path.isdir(candidate):
                continue
            real = os.path.realpath(candidate)
            if real.startswith(root + os.sep):
                return real
    return None


def _json_value(value, default):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return default
        return parsed
    return default


def _json_dump(value) -> str:
    return json.dumps(value if value is not None else [], ensure_ascii=False)


def _yaml_from_lab(lab: Lab) -> str:
    data = {
        "title": lab.name,
        "category": lab.category or "general",
        "difficulty": lab.difficulty or "beginner",
        "estimated_time": int(lab.duration_minutes or 60),
        "prerequisites": _json_value(lab.prerequisites, []),
        "learning_outcomes": _json_value(lab.objectives, []),
        "mapped_skills": _json_value(lab.mapped_skills, []),
        "assessment_criteria": _json_value(lab.assessment_criteria, []),
        "mitre_attack": _json_value(lab.mitre_attack, []),
        "description": lab.description or "",
        "scenario": lab.scenario or "",
        "flag": PLACEHOLDER_FLAG,
    }
    optional = {
        "hints": _json_value(lab.hints, []),
        "tools": _json_value(lab.tools, []),
        "hostnames": _json_value(lab.hostnames, []),
        "workbook": lab.workbook,
        "chapter_id": lab.chapter_id,
        "primary_competency": lab.primary_competency,
        "framework_refs": _json_value(lab.framework_refs, []),
        "measurable_outcome": lab.measurable_outcome,
        "content_version": lab.content_version,
        "week": lab.week,
        "show_target_ips": bool(lab.show_target_ips),
        "topology_nodes": _json_value(lab.topology_nodes, []),
        "ics_techniques": _json_value(lab.ics_techniques, []),
        "requires_kvm": bool(lab.requires_kvm),
        "counts_toward_certificate": bool(lab.counts_toward_certificate),
    }
    for key, value in optional.items():
        if value not in (None, "", [], {}):
            data[key] = value
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _replace_flag(yaml_text: str, flag: str) -> str:
    quoted = json.dumps(flag)
    if re.search(r"(?m)^flag\s*:", yaml_text):
        return re.sub(r"(?m)^flag\s*:.*$", f"flag: {quoted}", yaml_text, count=1)
    suffix = "" if yaml_text.endswith("\n") else "\n"
    return f"{yaml_text}{suffix}flag: {quoted}\n"


def _source_files(lab_dir: str) -> dict[str, bytes]:
    base = os.path.realpath(lab_dir)
    files: dict[str, bytes] = {}
    total = 0
    for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in SKIP_DIRS and not name.startswith(".")
        )
        for name in sorted(filenames):
            if (
                name in SKIP_FILES
                or name.startswith(".")
                or name.endswith(SKIP_SUFFIXES)
            ):
                continue
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                continue
            real = os.path.realpath(path)
            if not real.startswith(base + os.sep):
                continue
            relative = os.path.relpath(real, base).replace(os.sep, "/")
            if relative == "lab.yaml":
                continue
            with open(real, "rb") as handle:
                contents = handle.read()
            total += len(contents)
            if total > MAX_EXPORT_BYTES:
                raise ExerciseTransferError(
                    f"Exercise source exceeds the {MAX_EXPORT_BYTES // (1024 * 1024)} MB "
                    "export limit.",
                    status_code=413,
                )
            files[relative] = contents
    return files


def _readme(lab: Lab, flag_included: bool, warnings: list[str]) -> str:
    flag_note = (
        "The original flag is included. Treat this archive as a secret."
        if flag_included
        else (
            "The flag was replaced with `OCR{REPLACE_ME}`. The importer generates "
            "a new flag (or accepts one you provide), so copies do not share a flag."
        )
    )
    warning_text = "\n".join(f"- {line}" for line in warnings) or "- None."
    return f"""# Exercise export: {lab.name}

Format: `{FORMAT}` v{FORMAT_VERSION}
Source slug: `{lab.slug}`

## Import

1. Open **Admin → Exercises**.
2. Choose **Import Exercise**.
3. Select this ZIP, a track, and a level.
4. Leave the flag blank to generate a new one, or enter a new flag.
5. Review the draft before publishing it.

## Flag

{flag_note}

## Export notes

{warning_text}

The archive contains the authored source needed to rebuild the exercise:
`lab.yaml`, `docker-compose.yml`, and the files under the lab directory.

If `test.steps` or an entrypoint hardcodes the old flag, update it after import
to the new flag. Prefer reading the flag from the environment or `lab.yaml`.
"""


def export_lab_zip(
    db: Session,
    lab: Lab,
    *,
    include_flag: bool = False,
) -> tuple[bytes, str]:
    """Return ``(zip_bytes, filename)`` for one exercise.

    ``db`` is part of the signature so the caller can pass the same session used
    to load the lab; the exporter only reads the lab row.
    """
    lab_dir = _safe_lab_dir(lab.slug or "")
    warnings: list[str] = []
    files: dict[str, bytes] = {}
    lab_yaml = ""
    flag_included = False

    if lab_dir:
        files = _source_files(lab_dir)
        yaml_path = os.path.join(lab_dir, "lab.yaml")
        if os.path.isfile(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as handle:
                lab_yaml = handle.read()
        else:
            warnings.append("lab.yaml was missing; metadata was rebuilt from the database.")
    else:
        warnings.append(
            "The source directory was not found; exported metadata and compose "
            "only. Container files are not included."
        )

    if not lab_yaml:
        lab_yaml = _yaml_from_lab(lab)

    if include_flag:
        try:
            parsed = yaml.safe_load(lab_yaml) or {}
            flag_included = bool(
                str(parsed.get("flag") or "").strip()
                and str(parsed.get("flag")) != PLACEHOLDER_FLAG
            )
        except yaml.YAMLError:
            flag_included = False
        if not flag_included:
            warnings.append("No plaintext flag was available in the source lab.yaml.")
    else:
        lab_yaml = _replace_flag(lab_yaml, PLACEHOLDER_FLAG)

    files["lab.yaml"] = lab_yaml.encode("utf-8")
    if "docker-compose.yml" not in files:
        files["docker-compose.yml"] = (lab.compose_file or "services: {}\n").encode(
            "utf-8"
        )

    manifest = {
        "format": FORMAT,
        "format_version": FORMAT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "id": lab.id,
            "slug": lab.slug,
            "name": lab.name,
            "track": lab.level.track.slug if lab.level and lab.level.track else None,
            "level_number": lab.level.level_number if lab.level else None,
            "difficulty": lab.difficulty,
            "category": lab.category,
            "content_version": lab.content_version,
        },
        "flag_included": flag_included,
        "file_count": len(files),
        "files": sorted(files),
        "warnings": warnings,
        "import": {
            "endpoint": "/api/admin/labs/import",
            "required": ["track", "level_id"],
        },
    }
    files["export-manifest.json"] = json.dumps(
        manifest, indent=2, sort_keys=True
    ).encode("utf-8")
    files["EXPORT-README.md"] = _readme(lab, flag_included, warnings).encode("utf-8")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.writestr(name, files[name])
    filename = f"{lab.slug or 'exercise'}-export.zip"
    return buffer.getvalue(), filename


def _preview_zip(contents: bytes) -> tuple[dict, list[str], str]:
    if len(contents) > MAX_IMPORT_BYTES:
        raise ExerciseTransferError(
            f"ZIP too large (limit {MAX_IMPORT_BYTES // (1024 * 1024)} MB).",
            status_code=413,
        )
    try:
        archive = zipfile.ZipFile(io.BytesIO(contents))
    except zipfile.BadZipFile as exc:
        raise ExerciseTransferError("File is not a valid ZIP archive.") from exc

    entries = [name for name in archive.namelist() if not name.startswith("__MACOSX/")]
    top_level = {name.split("/")[0] for name in entries}
    strip_prefix = ""
    if len(top_level) == 1:
        candidate = next(iter(top_level))
        if any(name.startswith(candidate + "/") for name in entries):
            strip_prefix = candidate + "/"
    yaml_path = f"{strip_prefix}lab.yaml"
    if yaml_path not in entries:
        raise ExerciseTransferError("ZIP must contain lab.yaml.")
    try:
        lab_data = yaml.safe_load(archive.read(yaml_path).decode("utf-8")) or {}
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise ExerciseTransferError(f"Invalid lab.yaml: {exc}") from exc
    if not isinstance(lab_data, dict):
        raise ExerciseTransferError("lab.yaml must contain a mapping.")
    return lab_data, entries, strip_prefix


def _track_directory(track: Track) -> str:
    try:
        name = get_track_directory_name(track.slug)
    except Exception:
        name = ""
    name = os.path.basename(name or "")
    return name or track.name or track.slug.capitalize()


def _build_lab(
    lab_data: dict,
    *,
    slug: str,
    level: Level,
    lab_num: int,
    user_id: int,
    flag: str,
) -> Lab:
    workbook = (lab_data.get("workbook") or "").strip() or None
    chapter_id = (lab_data.get("chapter_id") or "").strip() or (
        chapter_id_for_workbook(workbook) if workbook else None
    )
    framework = {}
    try:
        framework = resolve_framework(slug, chapter_id, lab_data)
    except Exception:
        framework = {}
    scenario = lab_data.get("scenario") or ""
    objectives = lab_data.get("learning_outcomes", lab_data.get("objectives", []))
    lab = Lab(
        name=(lab_data.get("title") or lab_data.get("name") or slug)[:100],
        slug=slug,
        description=lab_data.get("description") or "",
        scenario=scenario,
        scenario_brief=(scenario[:150] + "...") if len(scenario) > 150 else scenario,
        difficulty=lab_data.get("difficulty") or "beginner",
        category=lab_data.get("category") or "general",
        duration_minutes=int(lab_data.get("estimated_time") or 60),
        level_id=level.id,
        compose_file="",
        objectives=_json_dump(objectives),
        prerequisites=_json_dump(lab_data.get("prerequisites", [])),
        mapped_skills=_json_dump(lab_data.get("mapped_skills", [])),
        assessment_criteria=_json_dump(lab_data.get("assessment_criteria", [])),
        hints=_json_dump(lab_data.get("hints", [])),
        tools=_json_dump(lab_data.get("tools", [])),
        hostnames=_json_dump(lab_data.get("hostnames", [])),
        flag_hash=hashlib.sha256(flag.encode("utf-8")).hexdigest() if flag else None,
        visibility="draft",
        created_by=user_id,
        is_active=True,
        sort_order=lab_num,
        workbook=workbook,
        chapter_id=chapter_id,
        primary_competency=lab_data.get("primary_competency")
        or framework.get("primary_competency"),
        framework_refs=_json_dump(
            lab_data.get("framework_refs") or framework.get("framework_refs") or []
        ),
        measurable_outcome=lab_data.get("measurable_outcome")
        or framework.get("measurable_outcome"),
        content_version=lab_data.get("content_version"),
        requires_kvm=bool(lab_data.get("requires_kvm", False)),
        counts_toward_certificate=bool(
            lab_data.get("counts_toward_certificate", True)
        ),
        show_target_ips=bool(lab_data.get("show_target_ips", False)),
        topology_nodes=_json_dump(lab_data.get("topology_nodes", [])),
        ics_techniques=_json_dump(lab_data.get("ics_techniques", [])),
        mitre_attack=_json_dump(lab_data.get("mitre_attack", [])),
        week=lab_data.get("week") or lab_data.get("phase"),
    )
    return lab


def import_lab_zip(
    db: Session,
    *,
    user_id: int,
    contents: bytes,
    track_slug: str,
    level_id: int,
    name_override: str | None = None,
    flag: str | None = None,
    reuse_flag: bool = False,
) -> dict:
    """Validate, extract, and register one exercise as a draft."""
    lab_data, _entries, _strip = _preview_zip(contents)
    name = (name_override or lab_data.get("title") or lab_data.get("name") or "").strip()
    if not name:
        raise ExerciseTransferError("lab.yaml must have a 'title' field.")

    level = db.query(Level).filter(Level.id == level_id).first()
    if level is None:
        raise ExerciseTransferError(f"Level {level_id} not found.")
    track = level.track
    if track is None or track.slug != track_slug:
        raise ExerciseTransferError(
            f"Level {level_id} does not belong to track '{track_slug}'."
        )

    lab_num = lab_upload.next_lab_number(level, track.slug)
    try:
        slug = lab_upload.generate_slug(
            name, track.slug, level.level_number, lab_num
        )
    except lab_upload.ZipValidationError as exc:
        raise ExerciseTransferError(str(exc)) from exc
    if db.query(Lab).filter(Lab.slug == slug).first():
        raise ExerciseTransferError(
            f"An exercise with slug '{slug}' already exists. Choose a different name.",
            status_code=409,
        )

    target_dir = os.path.join(
        os.path.realpath(getattr(lab_upload, "LABS_ROOT", _labs_root())),
        _track_directory(track),
        slug,
    )
    try:
        result = lab_upload.validate_and_extract_lab_zip(contents, target_dir)
    except lab_upload.ZipValidationError as exc:
        raise ExerciseTransferError(str(exc)) from exc

    existing_flag = str(result["lab_data"].get("flag") or "").strip()
    generated = False
    if flag and flag.strip():
        final_flag = flag.strip()
    elif reuse_flag and existing_flag and existing_flag != PLACEHOLDER_FLAG:
        final_flag = existing_flag
    else:
        final_flag = f"OCR{{{secrets.token_hex(16)}}}"
        generated = True

    try:
        yaml_path = os.path.join(target_dir, "lab.yaml")
        with open(yaml_path, "r", encoding="utf-8") as handle:
            yaml_text = handle.read()
        with open(yaml_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(_replace_flag(yaml_text, final_flag))

        lab = _build_lab(
            result["lab_data"],
            slug=slug,
            level=level,
            lab_num=lab_num,
            user_id=user_id,
            flag=final_flag,
        )
        lab.compose_file = result["compose_content"]
        db.add(lab)
        db.commit()
        db.refresh(lab)
    except Exception:
        db.rollback()
        shutil.rmtree(target_dir, ignore_errors=True)
        raise

    return {
        "id": lab.id,
        "slug": slug,
        "name": lab.name,
        "file_count": result["file_count"],
        "warnings": result["warnings"],
        "flag_generated": generated,
        "generated_flag": final_flag if generated else None,
        "visibility": lab.visibility,
    }
