"""Pre-flight checks for lab launches.

Production runs with ``LAB_ALLOW_ON_DEMAND_BUILD=false`` so a student launch
never triggers a slow Docker image build. This module answers two questions:

* Does this lab still have build-backed services whose images were never
  pre-built? The spawn endpoint refuses the launch with a plain-language
  message instead of handing the student a cryptic image-not-found error.
* Which labs recently hit that wall, and what exact command clears it? The
  admin health panel shows the recorded ``prebuild-labs.sh`` command.

Nothing here mutates lab state. A Docker check that cannot complete fails open:
a launch is never blocked just because the platform could not inspect an image.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import yaml

from app.models import ActivityEvent, Lab
from app.services.activity import EventTypes, log_activity

logger = logging.getLogger(__name__)

# Shown to a learner. Deliberately plain: no Docker jargon, no host paths, and
# no hint that the student could fix it themselves.
STUDENT_PREBUILDING_MESSAGE = (
    "This lab environment is still being prepared by your instructor. "
    "Please try again in a few minutes. If it stays unavailable, ask your "
    "instructor to finish setting up the exercise."
)

# How far back the admin health panel looks for refused launches. Long enough
# to survive a weekend, short enough that an old notice does not nag forever.
REMEMBER_DAYS = 30
# Keep the health card readable when many labs are waiting on a rebuild.
MAX_COMMANDS = 10


def on_demand_build_allowed() -> bool:
    """Whether a student spawn may build a missing image.

    Read from the manager at call time (not import time) so an operator's
    environment setting and tests both see the current value.
    """
    from app.services.docker_manager import DockerManager

    return bool(DockerManager.ALLOW_ON_DEMAND_BUILD)


def prebuild_command(lab_slug: str) -> str:
    """The exact command an operator runs from the repository root."""
    return f"scripts/prebuild-labs.sh --lab {lab_slug}"


def _services(compose_content: str) -> dict:
    try:
        data = yaml.safe_load(compose_content or "") or {}
    except Exception:
        return {}
    services = data.get("services")
    return services if isinstance(services, dict) else {}


def _candidate_tags(lab_slug: str, service_name: str, service: dict) -> list[str]:
    """Image names Compose may accept for a service that has to be built.

    ``prebuild-labs.sh`` builds the Compose project ``prebuild-<slug>`` and
    publishes ``ocr-lab/<slug>-<service>:latest``. Older checkouts also used
    ``<slug>-<service>:latest``. A compose file that pins ``image:`` is tagged
    at that name by ``compose build``.
    """
    tags: list[str] = []
    explicit = service.get("image")
    if explicit:
        tags.append(str(explicit))
    slug = lab_slug.lower()
    tags.extend(
        [
            f"prebuild-{slug}-{service_name}:latest",
            f"ocr-lab/{slug}-{service_name}:latest",
            f"{slug}-{service_name}:latest",
        ]
    )
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(tags))


def missing_built_services(
    lab_slug: str,
    compose_content: str,
    docker_client,
) -> Optional[list[str]]:
    """Return build-backed services with no local image.

    ``None`` means the check could not run (no Docker client or a daemon
    error), which callers must treat as "unknown, do not block". An empty list
    means every service that needs a build has an image available.
    """
    if docker_client is None:
        return None

    try:
        import docker as docker_sdk
    except Exception:  # pragma: no cover - docker is a hard dependency
        return None

    missing: list[str] = []
    for name, service in _services(compose_content).items():
        if not isinstance(service, dict) or "build" not in service:
            # An image-only service is pulled by Compose, not built here.
            continue

        found = False
        for tag in _candidate_tags(lab_slug, name, service):
            try:
                docker_client.images.get(tag)
                found = True
                break
            except docker_sdk.errors.ImageNotFound:
                continue
            except Exception as exc:
                logger.warning(
                    "Could not check image %s for lab %s: %s", tag, lab_slug, exc
                )
                return None
        if not found:
            missing.append(name)

    return missing


def record_prebuild_required(
    db,
    lab,
    user_id: int | None = None,
    ip_address: str | None = None,
) -> None:
    """Record a refused launch and log the exact command that fixes it.

    Deduplicated per lab per hour so a class of students clicking the same
    unfinished exercise does not flood the activity feed. The command is kept
    in ``detail`` so the admin health panel can show it verbatim.
    """
    slug = getattr(lab, "slug", None) or str(lab)
    command = prebuild_command(slug)
    logger.warning(
        "Lab %s is not pre-built; launch refused. Run on the server: %s",
        slug,
        command,
    )

    try:
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
        duplicate = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
                ActivityEvent.target_type == "lab",
                ActivityEvent.target_id == getattr(lab, "id", None),
                ActivityEvent.created_at >= cutoff,
            )
            .first()
        )
        if duplicate is not None:
            return

        log_activity(
            db,
            EventTypes.LAB_PREBUILD_REQUIRED,
            actor_id=user_id,
            target_type="lab",
            target_id=getattr(lab, "id", None),
            target_label=getattr(lab, "name", slug),
            detail={"lab_slug": slug, "command": command},
            ip_address=ip_address,
        )
    except Exception as exc:
        # A logging failure must never change the student-facing response.
        logger.warning("Could not record prebuild requirement for %s: %s", slug, exc)


def _recent_requests(db, days: int = REMEMBER_DAYS) -> dict[str, dict]:
    """Latest refused-launch record per lab slug within the window."""
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    rows = (
        db.query(ActivityEvent)
        .filter(
            ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
            ActivityEvent.created_at >= cutoff,
        )
        .order_by(ActivityEvent.created_at.desc())
        .limit(500)
        .all()
    )

    latest: dict[str, dict] = {}
    for row in rows:
        try:
            detail = json.loads(row.detail or "{}")
        except (TypeError, ValueError):
            detail = {}
        slug = detail.get("lab_slug")
        if not slug:
            continue
        entry = latest.get(slug)
        if entry is None:
            latest[slug] = {
                "lab_slug": slug,
                "command": detail.get("command") or prebuild_command(slug),
                "last_seen": row.created_at,
                "count": 1,
            }
        else:
            entry["count"] += 1
    return latest


def prebuild_health(db, docker_client) -> Optional[dict]:
    """Admin-health item for prebuilt lab images.

    Returns ``None`` when on-demand builds are allowed: there is nothing to
    warn about. When builds are disabled the item names every lab a student
    recently tried to open whose image is still missing, plus the exact
    ``prebuild-labs.sh`` command. Records that are now built are ignored, so
    the warning clears without the admin having to dismiss anything.
    """
    if on_demand_build_allowed():
        return None

    try:
        requests = _recent_requests(db)
    except Exception as exc:
        logger.warning("Could not read recent lab launch failures: %s", exc)
        return {
            "name": "Lab images",
            "status": "warning",
            "detail": "On-demand lab builds are disabled, but recent launch "
            "failures could not be read. Check the activity log.",
            "commands": [],
        }

    if not requests:
        return {
            "name": "Lab images",
            "status": "ok",
            "detail": "On-demand lab builds are disabled. No student has hit "
            "an unbuilt lab in the last %d days." % REMEMBER_DAYS,
            "commands": [],
        }

    try:
        labs = {
            lab.slug: lab
            for lab in db.query(Lab).filter(Lab.slug.in_(list(requests))).all()
        }
    except Exception as exc:
        logger.warning("Could not load labs for prebuild health: %s", exc)
        labs = {}

    pending: list[dict] = []
    unchecked = False
    for slug, entry in requests.items():
        lab = labs.get(slug)
        if lab is None:
            # The lab was removed or renamed after the refusal. Nothing to
            # prebuild, so do not keep showing an impossible command.
            continue
        missing = missing_built_services(slug, lab.compose_file or "", docker_client)
        if missing is None:
            unchecked = True
            pending.append(entry)
        elif missing:
            pending.append(entry)

    if not pending:
        return {
            "name": "Lab images",
            "status": "ok",
            "detail": "On-demand lab builds are disabled and every lab students "
            "recently requested is now built.",
            "commands": [],
        }

    pending.sort(key=lambda item: item.get("last_seen") or datetime.min, reverse=True)
    shown = pending[:MAX_COMMANDS]
    commands = [item["command"] for item in shown]
    attempts = sum(item["count"] for item in pending)

    if len(pending) == 1:
        detail = (
            f'"{pending[0]["lab_slug"]}" was requested before its image was built '
            f"({attempts} attempt{'s' if attempts != 1 else ''}). Run this exact "
            "command on the server, then refresh:"
        )
    else:
        detail = (
            f"{len(pending)} lab images are not built. Students tried to open "
            f"them {attempts} time{'s' if attempts != 1 else ''} in the last "
            f"{REMEMBER_DAYS} days. Run these exact commands on the server, then "
            "refresh:"
        )
    if len(pending) > len(shown):
        detail += f" Showing the {len(shown)} most recent; {len(pending) - len(shown)} more are waiting."
    if unchecked:
        detail += " Docker could not be inspected, so one or more may already be built."

    return {
        "name": "Lab images",
        "status": "warning",
        "detail": detail,
        "commands": commands,
    }
