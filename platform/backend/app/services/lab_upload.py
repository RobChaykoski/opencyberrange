"""
Lab ZIP upload validation and extraction service.

Handles the complete pipeline from receiving a ZIP file to having
validated files on disk ready for Docker to build and run.
"""

import glob
import io
import os
import re
import shutil
import zipfile
from typing import Optional

import yaml


MAX_ZIP_SIZE = 100 * 1024 * 1024       # 100 MB compressed
MAX_EXTRACTED_SIZE = 500 * 1024 * 1024  # 500 MB uncompressed
REQUIRED_FILES = ["lab.yaml", "docker-compose.yml"]
VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}

# Must stay in sync with SLUG_PATTERN in scripts/validate-lab.py and
# parse_lab_slug() in app/scripts/discover_labs.py. Discovery reads the level
# and lab number from the directory name, so a slug without them is skipped on
# the next database rebuild.
SLUG_PATTERN = re.compile(
    r"^[a-z]+(?:-[a-z]+)*-(?:\d+-\d+|midterm-\d+|final-\d+)-[a-z0-9-]+$"
)
MAX_SLUG_LENGTH = 80

# Every upload is extracted below this directory. The backend mounts the labs
# tree read-only at runtime, but the instructor upload path writes here.
LABS_ROOT = os.path.realpath(os.environ.get("OCR_LABS_ROOT", "/labs"))


def _safe_target_dir(target_dir: str) -> str:
    """Return a canonical extraction directory inside :data:`LABS_ROOT`.

    The caller supplies ``/labs/<track>/<slug>``. Each component is rebuilt as
    a single basename before the path is joined, so a caller-supplied value is
    never used directly to build a filesystem path.
    """
    raw = os.path.realpath(os.path.normpath(target_dir))
    if not raw.startswith(LABS_ROOT + os.sep):
        raise ZipValidationError("Lab upload target is outside the labs directory.")

    relative = raw[len(LABS_ROOT) + 1:]
    parts = [os.path.basename(part) for part in relative.split(os.sep) if part]
    if len(parts) < 2 or any(part in ("", ".", "..") for part in parts):
        raise ZipValidationError("Invalid lab upload target path.")

    candidate = os.path.join(LABS_ROOT, *parts)
    if os.path.realpath(candidate) != raw:
        raise ZipValidationError("Invalid lab upload target path.")
    return candidate


class ZipValidationError(Exception):
    """Raised when ZIP validation fails."""
    pass


def _slugify(text: str) -> str:
    """Lowercase, hyphen-separated slug fragment."""
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", base)


def generate_slug(name: str, track: str, level_number: int, lab_num: int) -> str:
    """Generate a discovery-compatible slug from a lab name, track and level.

    Returns e.g. 'web-4-1-my-ssh-exercise' from name='My SSH Exercise',
    track='web', level_number=4, lab_num=1.

    The level and lab number are part of the slug because discovery parses them
    from the directory name. Without them the uploaded lab works until the next
    database rebuild, then silently disappears.
    """
    track_slug = _slugify(track)
    if not track_slug:
        raise ZipValidationError(f"Track '{track}' does not produce a usable slug")
    try:
        level_number = int(level_number)
        lab_num = int(lab_num)
    except (TypeError, ValueError):
        raise ZipValidationError("Level and lab number must be integers")
    if level_number < 1 or lab_num < 1:
        raise ZipValidationError("Level and lab number must be positive")

    prefix = f"{track_slug}-{level_number}-{lab_num}-"
    base = _slugify(name)
    if not base:
        raise ZipValidationError(
            f"Lab name '{name}' does not produce a usable slug. Use at least "
            "one letter or number."
        )

    # Cap the total length by trimming the descriptive tail, never the prefix.
    available = MAX_SLUG_LENGTH - len(prefix)
    if available < 1:
        raise ZipValidationError(
            f"Track and level produce a slug prefix that is too long: '{prefix}'"
        )
    base = base[:available].rstrip("-") or "exercise"

    slug = prefix + base
    if not SLUG_PATTERN.match(slug):
        raise ZipValidationError(
            f"Generated slug '{slug}' is invalid. Lab name must start with "
            f"a letter and contain only letters, numbers, spaces, and hyphens."
        )
    return slug


def slug_base(slug: str, track_slug: str) -> str:
    """Descriptive tail of a conforming slug ('web-4-1-xss' -> 'xss')."""
    match = re.match(rf"^{re.escape(track_slug)}-\d+-\d+-(.+)$", slug or "")
    return match.group(1) if match else ""


def next_lab_number(level, track_slug: str) -> int:
    """Next free lab number in *level*.

    Uses both ``sort_order`` and the number embedded in existing slugs so
    legacy uploads stored with ``sort_order=0`` do not collide.
    """
    pattern = re.compile(rf"^{re.escape(track_slug)}-{level.level_number}-(\d+)-")
    used = [lab.sort_order or 0 for lab in level.labs]
    for lab in level.labs:
        match = pattern.match(lab.slug or "")
        if match:
            used.append(int(match.group(1)))
    return max(used, default=0) + 1


def relocate_lab(lab, new_level, db, labs_dir: Optional[str] = None) -> str:
    """Move a UI-created lab to *new_level*, renaming its directory and slug.

    Discovery derives a lab's level from its directory name, so a lab whose
    level changes must change its slug too, or the next scan puts it back where
    it was. Returns the new slug; the caller commits *lab*.
    """
    track = new_level.track
    if track is None:
        raise ZipValidationError("Level has no track")

    old_track_slug = ""
    if lab.level is not None and lab.level.track is not None:
        old_track_slug = lab.level.track.slug
    if not old_track_slug:
        old_track_slug = (lab.slug or "").split("-")[0]

    base = slug_base(lab.slug, old_track_slug) or _slugify(lab.name)
    if not base:
        raise ZipValidationError(
            f"Lab name '{lab.name}' does not produce a usable slug"
        )

    lab_num = next_lab_number(new_level, track.slug)
    new_slug = generate_slug(base, track.slug, new_level.level_number, lab_num)
    if new_slug == lab.slug:
        return new_slug

    clash = db.query(type(lab)).filter(
        type(lab).slug == new_slug,
        type(lab).id != lab.id,
    ).first()
    if clash:
        raise ZipValidationError(f"Slug '{new_slug}' is already in use")

    # A running session still points at the old directory; move it later.
    from app.models import LabSession
    active = db.query(LabSession).filter(
        LabSession.lab_id == lab.id,
        LabSession.status.in_(["starting", "running", "stopping"]),
    ).count()
    if active:
        raise ZipValidationError(
            f"Cannot move the exercise while {active} session(s) are active"
        )

    labs_root = labs_dir or os.environ.get("LABS_DIR", "/labs")
    old_dir = None
    for candidate in glob.glob(os.path.join(labs_root, "*", lab.slug or "")):
        if os.path.isdir(candidate):
            old_dir = candidate
            break

    if old_dir:
        from app.services.docker_manager import get_track_directory_name
        track_dir = os.path.basename(get_track_directory_name(track.slug))
        safe_slug = os.path.basename(new_slug)
        new_dir = os.path.join(labs_root, track_dir, safe_slug)
        if os.path.exists(new_dir):
            raise ZipValidationError(f"Directory already exists: {new_dir}")
        os.makedirs(os.path.dirname(new_dir), exist_ok=True)
        os.rename(old_dir, new_dir)

    lab.slug = new_slug
    lab.sort_order = lab_num
    return new_slug


def validate_and_extract_lab_zip(contents: bytes, target_dir: str) -> dict:
    """Validate a lab ZIP file and extract it to target_dir.

    Args:
        contents: Raw bytes of the uploaded ZIP file.
        target_dir: Absolute path to extract files into (must not exist).

    Returns:
        dict with keys:
            lab_data:        parsed lab.yaml as dict
            compose_content: raw docker-compose.yml string
            file_count:      number of files extracted
            warnings:        list of non-fatal warning strings

    Raises:
        ZipValidationError: on any validation failure.
    """
    target_dir = _safe_target_dir(target_dir)
    warnings = []

    # --- Size check ---
    if len(contents) > MAX_ZIP_SIZE:
        raise ZipValidationError(
            f"ZIP file too large ({len(contents) // (1024*1024)} MB). "
            f"Maximum is {MAX_ZIP_SIZE // (1024*1024)} MB."
        )

    # --- Open ZIP ---
    try:
        zf = zipfile.ZipFile(io.BytesIO(contents))
    except zipfile.BadZipFile:
        raise ZipValidationError("File is not a valid ZIP archive.")

    # --- Zip bomb check ---
    total_uncompressed = sum(info.file_size for info in zf.infolist())
    if total_uncompressed > MAX_EXTRACTED_SIZE:
        raise ZipValidationError(
            f"Uncompressed size too large ({total_uncompressed // (1024*1024)} MB). "
            f"Maximum is {MAX_EXTRACTED_SIZE // (1024*1024)} MB."
        )

    # --- Path traversal check (pre-extraction) ---
    for name in zf.namelist():
        if ".." in name or name.startswith("/"):
            raise ZipValidationError(f"Unsafe path in ZIP: {name}")

    # --- Filter out macOS resource forks ---
    entries = [n for n in zf.namelist() if not n.startswith("__MACOSX/")]

    # --- Detect single-root-directory wrapper ---
    top_level = set()
    for name in entries:
        parts = name.split("/")
        top_level.add(parts[0])

    strip_prefix = ""
    if len(top_level) == 1:
        candidate = list(top_level)[0]
        if any(n.startswith(candidate + "/") for n in entries):
            strip_prefix = candidate + "/"

    # --- Build adjusted name set ---
    adjusted = set()
    for name in entries:
        if name.startswith(strip_prefix):
            rel = name[len(strip_prefix):]
            if rel:
                adjusted.add(rel)

    # --- Required files ---
    for req in REQUIRED_FILES:
        if req not in adjusted:
            raise ZipValidationError(
                f"Missing required file: {req}. "
                f"Your ZIP must contain both lab.yaml and docker-compose.yml."
            )

    # --- Check for at least one Dockerfile ---
    has_dockerfile = any(
        os.path.basename(n) == "Dockerfile" for n in adjusted
    )
    if not has_dockerfile:
        warnings.append(
            "No Dockerfile found. Exercises typically need a containers/ "
            "directory with at least one Dockerfile."
        )

    # --- Parse lab.yaml ---
    yaml_raw = zf.read(strip_prefix + "lab.yaml").decode("utf-8")
    try:
        lab_data = yaml.safe_load(yaml_raw) or {}
    except yaml.YAMLError as e:
        raise ZipValidationError(f"Invalid lab.yaml syntax: {e}")

    if not (lab_data.get("title") or lab_data.get("name")):
        raise ZipValidationError(
            "lab.yaml must have a 'title' field (legacy 'name' is accepted)."
        )

    metadata_fields = (
        "title",
        "category",
        "difficulty",
        "estimated_time",
        "prerequisites",
        "learning_outcomes",
        "mapped_skills",
        "assessment_criteria",
    )
    missing_metadata = [key for key in metadata_fields if key not in lab_data]
    if missing_metadata:
        warnings.append(
            "Lab metadata is incomplete (missing: "
            + ", ".join(missing_metadata)
            + "). See docs/LAB-METADATA-SCHEMA.md for the canonical schema."
        )

    if not lab_data.get("flag"):
        warnings.append(
            "No 'flag' field in lab.yaml. The exercise won't be completable "
            "without a flag for students to submit."
        )

    test_config = lab_data.get("test", {})
    if not test_config.get("steps"):
        warnings.append(
            "No 'test.steps' in lab.yaml. The automated tester can only "
            "perform generic checks without custom solve steps."
        )

    difficulty = lab_data.get("difficulty", "beginner")
    if difficulty not in VALID_DIFFICULTIES:
        warnings.append(
            f"Unknown difficulty '{difficulty}'. "
            f"Valid values: {', '.join(sorted(VALID_DIFFICULTIES))}. "
            f"Defaulting to 'beginner'."
        )
        lab_data["difficulty"] = "beginner"

    # --- Parse docker-compose.yml ---
    compose_raw = zf.read(strip_prefix + "docker-compose.yml").decode("utf-8")
    try:
        compose_data = yaml.safe_load(compose_raw) or {}
    except yaml.YAMLError as e:
        raise ZipValidationError(f"Invalid docker-compose.yml syntax: {e}")

    services = compose_data.get("services", {})
    if not services:
        raise ZipValidationError(
            "docker-compose.yml must define at least one service."
        )

    for svc_name, svc_def in services.items():
        labels = svc_def.get("labels", {})
        if "ip_offset" not in labels:
            warnings.append(
                f"Service '{svc_name}' missing 'labels.ip_offset'. "
                f"Container won't get a static IP address."
            )
        build = svc_def.get("build", {})
        if isinstance(build, dict):
            ctx = build.get("context", "")
            # Normalize: remove leading ./ for comparison
            ctx_clean = ctx.lstrip("./")
            if ctx_clean and ctx_clean + "/" not in adjusted and not any(
                a.startswith(ctx_clean + "/") for a in adjusted
            ):
                warnings.append(
                    f"Service '{svc_name}' build context '{ctx}' "
                    f"not found in ZIP."
                )

    # --- Extract to disk ---
    if os.path.exists(target_dir):
        raise ZipValidationError(
            "Lab directory already exists on disk. "
            "If re-uploading, delete the existing exercise first."
        )

    os.makedirs(target_dir, mode=0o755)
    file_count = 0

    try:
        for info in zf.infolist():
            if info.filename.startswith("__MACOSX/"):
                continue
            if not info.filename.startswith(strip_prefix):
                continue
            relative = info.filename[len(strip_prefix):]
            if not relative:
                continue

            # Rebuild the relative path from single path components. The
            # basename call is an explicit sanitizer for every component, so a
            # crafted ZIP entry cannot introduce "..", an absolute path, or a
            # drive-relative path. Subdirectories are preserved.
            parts = [part for part in relative.split("/") if part]
            if not parts or any(part in (".", "..") for part in parts):
                raise ZipValidationError(f"Unsafe path in ZIP: {relative}")
            safe_parts = [os.path.basename(part) for part in parts]
            target_path = os.path.join(target_dir, *safe_parts)
            resolved = os.path.realpath(target_path)

            # Post-extraction path traversal check. commonpath is exact, unlike
            # a prefix test that would accept a sibling such as "<dir>-evil".
            try:
                inside_root = os.path.commonpath(
                    [os.path.realpath(target_dir), resolved]
                ) == os.path.realpath(target_dir)
            except ValueError:
                inside_root = False
            if not inside_root:
                raise ZipValidationError(f"Path traversal detected: {relative}")

            if relative.endswith("/"):
                os.makedirs(target_path, mode=0o755, exist_ok=True)
            else:
                parent = os.path.dirname(target_path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, mode=0o755, exist_ok=True)
                with open(target_path, "wb") as f:
                    f.write(zf.read(info.filename))
                # Make scripts/entrypoints executable
                if relative.endswith((".sh", ".py")):
                    os.chmod(target_path, 0o755)
                else:
                    os.chmod(target_path, 0o644)
                file_count += 1

    except ZipValidationError:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise ZipValidationError(f"Extraction failed: {e}")

    return {
        "lab_data": lab_data,
        "compose_content": compose_raw,
        "file_count": file_count,
        "warnings": warnings,
    }
