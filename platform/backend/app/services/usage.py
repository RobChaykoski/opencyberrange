"""Aggregate platform usage for the public tracker and the admin detail view.

The payload is aggregate-only. Learner identifiers, usernames, emails, IPs, and
per-learner rows never leave this service. When ``public`` is true, small source
and per-lab learner counts are marked as suppressed so a small group cannot be
identified from the dashboard.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import ActivityEvent, Lab, LabCompletion, LabSession, User
from app.services import attribution, settings_service
from app.services.activity import EventTypes

DEFAULT_MIN_COHORT_SIZE = 5


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() + "Z" if value else None


def _minimum_cohort_size(db: Session) -> int:
    raw = settings_service.get_setting_fresh(
        db, "analytics_min_cohort_size", str(DEFAULT_MIN_COHORT_SIZE)
    )
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = DEFAULT_MIN_COHORT_SIZE
    return max(0, min(value, 1000))


def _delta(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100.0, 1)


def _detail(row: ActivityEvent) -> dict:
    if not row.detail:
        return {}
    try:
        value = json.loads(row.detail)
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _source_of(user: Optional[User]) -> str:
    if user is None:
        return "unknown"
    return attribution.normalize_source(user.registration_source)


def _count_registrations(db: Session, start: datetime, end: Optional[datetime] = None) -> int:
    query = db.query(func.count(User.id)).filter(User.created_at >= start)
    if end is not None:
        query = query.filter(User.created_at < end)
    return int(query.scalar() or 0)


def _count_scans(db: Session, start: datetime, end: Optional[datetime] = None) -> int:
    query = db.query(func.count(ActivityEvent.id)).filter(
        ActivityEvent.event_type == EventTypes.QR_SCANNED,
        ActivityEvent.created_at >= start,
    )
    if end is not None:
        query = query.filter(ActivityEvent.created_at < end)
    return int(query.scalar() or 0)


def _count_completions(db: Session, start: datetime, end: Optional[datetime] = None) -> int:
    query = db.query(func.count(LabCompletion.id)).filter(
        LabCompletion.completed_at >= start
    )
    if end is not None:
        query = query.filter(LabCompletion.completed_at < end)
    return int(query.scalar() or 0)


def _active_learners(db: Session, start: datetime, end: Optional[datetime] = None) -> int:
    query = db.query(func.count(func.distinct(LabCompletion.user_id))).filter(
        LabCompletion.completed_at >= start
    )
    if end is not None:
        query = query.filter(LabCompletion.completed_at < end)
    return int(query.scalar() or 0)


def _daily_series(
    since: datetime,
    registrations: list[User],
    scans: list[ActivityEvent],
    completions: list[LabCompletion],
) -> list[dict]:
    series: dict[date, dict] = {}
    today = _now().date()
    cursor = since.date()
    while cursor <= today:
        series[cursor] = {"date": cursor.isoformat(), "registrations": 0, "qr_scans": 0, "completions": 0}
        cursor += timedelta(days=1)

    for row in registrations:
        if row.created_at and row.created_at.date() in series:
            series[row.created_at.date()]["registrations"] += 1
    for row in scans:
        if row.created_at and row.created_at.date() in series:
            series[row.created_at.date()]["qr_scans"] += 1
    for row in completions:
        if row.completed_at and row.completed_at.date() in series:
            series[row.completed_at.date()]["completions"] += 1
    return [series[key] for key in sorted(series)]


def _suppressed(count: int, minimum: int, public: bool) -> bool:
    return public and minimum > 0 and 0 < count < minimum


def build_usage(db: Session, *, days: int = 30, public: bool = True) -> dict:
    days = max(1, min(int(days), 365))
    now = _now()
    since = now - timedelta(days=days - 1)
    previous_since = since - timedelta(days=days)
    minimum = _minimum_cohort_size(db)

    registrations = (
        db.query(User)
        .filter(User.created_at >= since)
        .order_by(User.created_at.asc())
        .all()
    )
    scans = (
        db.query(ActivityEvent)
        .filter(
            ActivityEvent.event_type == EventTypes.QR_SCANNED,
            ActivityEvent.created_at >= since,
        )
        .order_by(ActivityEvent.created_at.asc())
        .all()
    )
    completion_rows = (
        db.query(LabCompletion, Lab)
        .join(Lab, Lab.id == LabCompletion.lab_id)
        .filter(LabCompletion.completed_at >= since)
        .order_by(LabCompletion.completed_at.asc())
        .all()
    )
    completions = [row for row, _lab in completion_rows]
    session_rows = (
        db.query(LabSession.user_id, LabSession.lab_id)
        .filter(LabSession.started_at >= since)
        .distinct()
        .all()
    )

    user_ids = {row.user_id for row in completions}
    users = {
        user.id: user
        for user in db.query(User).filter(User.id.in_(user_ids)).all()
    } if user_ids else {}

    total_registrations = len(registrations)
    total_scans = len(scans)
    total_completions = len(completions)
    total_active = len({row.user_id for row in completions})

    previous_registrations = _count_registrations(db, previous_since, since)
    previous_scans = _count_scans(db, previous_since, since)
    previous_completions = _count_completions(db, previous_since, since)
    previous_active = _active_learners(db, previous_since, since)

    # Week-over-week cards use the last seven complete days against the seven
    # before them, independent of the selected window.
    week_start = now - timedelta(days=7)
    previous_week_start = week_start - timedelta(days=7)
    week = {
        "since": _iso(week_start),
        "registrations": {
            "current": _count_registrations(db, week_start),
            "previous": _count_registrations(db, previous_week_start, week_start),
        },
        "qr_scans": {
            "current": _count_scans(db, week_start),
            "previous": _count_scans(db, previous_week_start, week_start),
        },
        "completions": {
            "current": _count_completions(db, week_start),
            "previous": _count_completions(db, previous_week_start, week_start),
        },
        "active_learners": {
            "current": _active_learners(db, week_start),
            "previous": _active_learners(db, previous_week_start, week_start),
        },
    }
    for item in week.values():
        if isinstance(item, dict) and "current" in item:
            item["delta_pct"] = _delta(item["current"], item["previous"])

    source_stats: dict[str, dict] = defaultdict(
        lambda: {"registrations": 0, "scans": 0, "completions": 0, "campaigns": Counter()}
    )
    for row in registrations:
        key = _source_of(row)
        source_stats[key]["registrations"] += 1
        if row.registration_campaign:
            source_stats[key]["campaigns"][row.registration_campaign] += 1
    for row in scans:
        detail = _detail(row)
        key = attribution.normalize_source(detail.get("source"))
        source_stats[key]["scans"] += 1
    for row in completions:
        key = _source_of(users.get(row.user_id))
        source_stats[key]["completions"] += 1

    source_rows = []
    for key, stats in source_stats.items():
        suppressed = _suppressed(stats["registrations"], minimum, public)
        source_rows.append(
            {
                "key": key,
                "label": attribution.source_label(key),
                "registrations": None if suppressed else stats["registrations"],
                "registrations_suppressed": suppressed,
                "scans": stats["scans"],
                "completions": stats["completions"],
                "share": None
                if suppressed
                else (
                    round(stats["registrations"] / total_registrations, 4)
                    if total_registrations
                    else 0.0
                ),
            }
        )
    source_rows.sort(key=lambda item: (-(item["registrations"] or 0), item["label"]))

    campaigns: dict[str, dict] = defaultdict(lambda: {"scans": 0, "registrations": 0})
    for row in scans:
        detail = _detail(row)
        campaign = attribution.normalize_campaign(detail.get("campaign")) or "direct"
        campaigns[campaign]["scans"] += 1
    for row in registrations:
        campaign = row.registration_campaign or "direct"
        campaigns[campaign]["registrations"] += 1
    campaign_rows = []
    for campaign, stats in campaigns.items():
        suppressed = _suppressed(stats["registrations"], minimum, public)
        campaign_rows.append(
            {
                "campaign": campaign,
                "scans": stats["scans"],
                "registrations": None if suppressed else stats["registrations"],
                "registrations_suppressed": suppressed,
                "conversion": round(stats["registrations"] / stats["scans"], 4)
                if stats["scans"]
                else None,
            }
        )
    campaign_rows.sort(key=lambda item: (-item["scans"], item["campaign"]))

    lab_stats: dict[int, dict] = {}
    for row, lab in completion_rows:
        stats = lab_stats.setdefault(
            lab.id,
            {
                "lab_id": lab.id,
                "slug": lab.slug,
                "name": lab.name,
                "category": lab.category or "general",
                "difficulty": lab.difficulty or "beginner",
                "completions": 0,
                "learners": set(),
                "attempts": [],
                "hints": [],
                "minutes": [],
                "first_attempt": 0,
                "last_completed_at": None,
            },
        )
        stats["completions"] += 1
        stats["learners"].add(row.user_id)
        stats["attempts"].append(int(row.attempts or 1))
        stats["hints"].append(int(row.hints_used or 0))
        if row.time_spent_minutes is not None:
            stats["minutes"].append(int(row.time_spent_minutes))
        if int(row.attempts or 1) <= 1:
            stats["first_attempt"] += 1
        if row.completed_at and (
            stats["last_completed_at"] is None
            or row.completed_at > stats["last_completed_at"]
        ):
            stats["last_completed_at"] = row.completed_at

    started_pairs: dict[int, set] = defaultdict(set)
    for user_id, lab_id in session_rows:
        started_pairs[lab_id].add(user_id)

    lab_rows = []
    for stats in lab_stats.values():
        learners = len(stats["learners"])
        suppressed = _suppressed(learners, minimum, public)
        started = len(started_pairs.get(stats["lab_id"], set()))
        started_suppressed = _suppressed(started, minimum, public)
        attempts = stats["attempts"]
        minutes = stats["minutes"]
        lab_rows.append(
            {
                "slug": stats["slug"],
                "name": stats["name"],
                "category": stats["category"],
                "difficulty": stats["difficulty"],
                "completions": stats["completions"],
                "learners": None if suppressed else learners,
                "learners_suppressed": suppressed,
                "attempts_avg": round(sum(attempts) / len(attempts), 2) if attempts else None,
                "hints_avg": round(sum(stats["hints"]) / len(stats["hints"]), 2)
                if stats["hints"]
                else None,
                "median_minutes": round(statistics.median(minutes), 1) if minutes else None,
                "first_attempt_rate": round(stats["first_attempt"] / stats["completions"], 3)
                if stats["completions"]
                else None,
                "started_learners": None if started_suppressed else started,
                "started_learners_suppressed": started_suppressed,
                "completion_rate": None
                if suppressed or started_suppressed or not started
                else round(learners / started, 3),
                "last_completed_at": _iso(stats["last_completed_at"]),
            }
        )
    lab_rows.sort(key=lambda item: (-item["completions"], item["name"]))
    total_labs = len(lab_rows)
    lab_rows = lab_rows[:100]

    # Movers compare the last 7 days with the 7 before them.
    source_movers = []
    current_source = Counter(
        _source_of(row)
        for row in db.query(User).filter(User.created_at >= week_start).all()
    )
    previous_source = Counter(
        _source_of(row)
        for row in db.query(User).filter(
            User.created_at >= previous_week_start, User.created_at < week_start
        ).all()
    )
    for key in set(current_source) | set(previous_source):
        source_movers.append(
            {
                "key": key,
                "label": attribution.source_label(key),
                "current": current_source[key],
                "previous": previous_source[key],
                "delta_pct": _delta(current_source[key], previous_source[key]),
            }
        )
    source_movers.sort(key=lambda item: (-(item["current"] - item["previous"]), -item["current"]))

    lab_movers = []
    current_labs = Counter()
    previous_labs = Counter()
    for row in db.query(LabCompletion, Lab).join(Lab, Lab.id == LabCompletion.lab_id).filter(
        LabCompletion.completed_at >= previous_week_start
    ).all():
        target = current_labs if row[0].completed_at >= week_start else previous_labs
        target[row[1].name] += 1
    for name in set(current_labs) | set(previous_labs):
        lab_movers.append(
            {
                "name": name,
                "current": current_labs[name],
                "previous": previous_labs[name],
                "delta_pct": _delta(current_labs[name], previous_labs[name]),
            }
        )
    lab_movers.sort(key=lambda item: (-(item["current"] - item["previous"]), -item["current"]))

    recent_rows = (
        db.query(ActivityEvent)
        .filter(
            ActivityEvent.event_type.in_(
                (EventTypes.USER_REGISTERED, EventTypes.LAB_COMPLETED, EventTypes.QR_SCANNED)
            )
        )
        .order_by(ActivityEvent.created_at.desc())
        .limit(12)
        .all()
    )
    recent = []
    for row in recent_rows:
        if row.event_type == EventTypes.USER_REGISTERED:
            label = f"New {attribution.source_label(_detail(row).get('source'))} registration"
            kind = "registration"
        elif row.event_type == EventTypes.LAB_COMPLETED:
            label = f"Completed {row.target_label or 'a lab'}"
            kind = "completion"
        else:
            label = f"QR scan: {row.target_label or 'campaign'}"
            kind = "scan"
        recent.append({"kind": kind, "label": label, "at": _iso(row.created_at)})

    return {
        "generated_at": _iso(now),
        "window_days": days,
        "since": _iso(since),
        "public": public,
        "minimum_cohort_size": minimum,
        "totals": {
            "registrations": {
                "value": total_registrations,
                "previous": previous_registrations,
                "delta_pct": _delta(total_registrations, previous_registrations),
            },
            "qr_scans": {
                "value": total_scans,
                "previous": previous_scans,
                "delta_pct": _delta(total_scans, previous_scans),
            },
            "completions": {
                "value": total_completions,
                "previous": previous_completions,
                "delta_pct": _delta(total_completions, previous_completions),
            },
            "active_learners": {
                "value": total_active,
                "previous": previous_active,
                "delta_pct": _delta(total_active, previous_active),
            },
        },
        "week": week,
        "daily": _daily_series(since, registrations, scans, completions),
        "sources": source_rows,
        "campaigns": campaign_rows[:20],
        "labs": {"total": total_labs, "returned": len(lab_rows), "items": lab_rows},
        "movers": {"sources": source_movers[:5], "labs": lab_movers[:5]},
        "recent": recent,
    }
