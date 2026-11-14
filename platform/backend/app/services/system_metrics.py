"""Sampled host and platform metrics for the admin System view."""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import LabSession, SystemMetric
from app.services.docker_manager import DockerManager

logger = logging.getLogger(__name__)

RETENTION_DAYS = 30
MAX_POINTS = 180
SERIES_FIELDS = (
    "load1",
    "load5",
    "load15",
    "mem_used_mb",
    "disk_used_gb",
    "active_sessions",
    "rangebox_count",
    "docker_containers",
    "docker_images",
    "db_connections",
)


def _naive_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _memory_mb() -> tuple[int, int]:
    total_kb = available_kb = 0
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    available_kb = int(line.split()[1])
    except OSError:
        pass
    total_mb = total_kb // 1024
    used_mb = max(0, (total_kb - available_kb) // 1024) if available_kb else 0
    return total_mb, used_mb


def _load() -> tuple[float, float, float]:
    try:
        return tuple(float(value) for value in os.getloadavg())  # type: ignore[return-value]
    except (OSError, AttributeError):
        return 0.0, 0.0, 0.0


def _docker_counts() -> tuple[int, int, int]:
    manager = None
    try:
        manager = DockerManager()
        if not manager.client:
            return 0, 0, 0
        containers = manager.client.containers.list()
        images = manager.client.images.list()
        rangeboxes = manager.client.containers.list(
            filters={"label": "ocr.role=rangebox"}
        )
        return len(containers), len(images), len(rangeboxes)
    except Exception as exc:
        logger.debug("Docker metrics unavailable: %s", exc)
        return 0, 0, 0
    finally:
        if manager is not None:
            try:
                manager.close()
            except Exception:
                pass


def collect(db: Session) -> dict:
    load1, load5, load15 = _load()
    total_mb, used_mb = _memory_mb()
    try:
        usage = shutil.disk_usage("/")
        disk_total_gb = round(usage.total / (1024 ** 3), 2)
        disk_used_gb = round(usage.used / (1024 ** 3), 2)
    except OSError:
        disk_total_gb = disk_used_gb = 0.0

    db_connections = 0
    try:
        db_connections = int(
            db.execute(
                text(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE datname = current_database()"
                )
            ).scalar()
            or 0
        )
    except Exception:
        pass

    active_sessions = 0
    try:
        active_sessions = (
            db.query(LabSession)
            .filter(LabSession.status.in_(("starting", "running")))
            .count()
        )
    except Exception:
        db.rollback()

    docker_containers, docker_images, rangeboxes = _docker_counts()
    payload = {
        "load1": round(load1, 3),
        "load5": round(load5, 3),
        "load15": round(load15, 3),
        "cpu_count": os.cpu_count() or 1,
        "mem_total_mb": total_mb,
        "mem_used_mb": used_mb,
        "disk_total_gb": disk_total_gb,
        "disk_used_gb": disk_used_gb,
        "active_sessions": active_sessions,
        "rangebox_count": rangeboxes,
        "docker_containers": docker_containers,
        "docker_images": docker_images,
        "db_connections": db_connections,
    }
    return payload


def sample_once() -> dict:
    db = SessionLocal()
    try:
        payload = collect(db)
        row = SystemMetric(**payload)
        db.add(row)
        cutoff = _naive_now() - timedelta(days=RETENTION_DAYS)
        db.query(SystemMetric).filter(SystemMetric.created_at < cutoff).delete(
            synchronize_session=False
        )
        db.commit()
        db.refresh(row)
        return {"id": row.id, "created_at": row.created_at.isoformat(), **payload}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _row_payload(row: SystemMetric) -> dict:
    payload = {
        "id": row.id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
    for field in SERIES_FIELDS:
        payload[field] = getattr(row, field)
    payload["cpu_count"] = row.cpu_count
    payload["mem_total_mb"] = row.mem_total_mb
    payload["disk_total_gb"] = row.disk_total_gb
    return payload


def _downsample(rows: list[SystemMetric]) -> list[dict]:
    if len(rows) <= MAX_POINTS:
        return [_row_payload(row) for row in rows]
    bucket_size = len(rows) / MAX_POINTS
    result = []
    for index in range(MAX_POINTS):
        start = int(index * bucket_size)
        end = max(start + 1, int((index + 1) * bucket_size))
        bucket = rows[start:end]
        if not bucket:
            continue
        row = bucket[-1]
        payload = _row_payload(row)
        for field in SERIES_FIELDS:
            values = [getattr(item, field) for item in bucket if getattr(item, field) is not None]
            if values:
                payload[field] = round(sum(values) / len(values), 3)
        result.append(payload)
    return result


def history(db: Session, hours: int = 24) -> dict:
    hours = min(max(int(hours), 1), 24 * 30)
    since = _naive_now() - timedelta(hours=hours)
    rows = (
        db.query(SystemMetric)
        .filter(SystemMetric.created_at >= since)
        .order_by(SystemMetric.created_at.asc())
        .all()
    )
    series = _downsample(rows)
    latest = rows[-1] if rows else None
    return {
        "hours": hours,
        "sample_count": len(rows),
        "latest": _row_payload(latest) if latest else None,
        "series": series,
    }
