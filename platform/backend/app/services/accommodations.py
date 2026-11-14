"""Per-student accessibility accommodations."""

from __future__ import annotations

from app.models import AccommodationEvent, UserAccommodation
from app.services import settings_service

MIN_MULTIPLIER = 1.0
MAX_MULTIPLIER = 3.0
MAX_EXTENSION_DAYS = 365


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def global_percent(db) -> int:
    """Operator-wide timed-session percentage from platform settings."""
    try:
        value = int(
            settings_service.get_setting(db, "session_accommodation_percent", "100")
        )
    except (TypeError, ValueError):
        value = 100
    return _clamp_int(value, 100, 300)


def get_record(db, user_id: int) -> UserAccommodation | None:
    return (
        db.query(UserAccommodation)
        .filter(UserAccommodation.user_id == user_id)
        .first()
    )


def effective_multiplier(db, user_id: int | None) -> float:
    """The learner's multiplier, or 1.0 when no record exists."""
    if not user_id:
        return 1.0
    record = get_record(db, user_id)
    if record is None:
        return 1.0
    return max(MIN_MULTIPLIER, min(MAX_MULTIPLIER, float(record.time_multiplier)))


def effective_percent(db, user_id: int | None) -> int:
    """Timed-session percentage for this learner.

    A per-student record replaces the global setting; without one the operator
    setting still applies, preserving the existing institution-wide control.
    """
    if user_id and get_record(db, user_id) is not None:
        return _clamp_int(round(effective_multiplier(db, user_id) * 100), 100, 300)
    return global_percent(db)


def extension_days(db, user_id: int | None) -> int:
    if not user_id:
        return 0
    record = get_record(db, user_id)
    if record is None:
        return 0
    return _clamp_int(int(record.due_date_extension_days or 0), 0, MAX_EXTENSION_DAYS)


def set_accommodation(
    db,
    *,
    user_id: int,
    actor_id: int | None,
    time_multiplier: float,
    due_date_extension_days: int,
    notes: str = "",
) -> UserAccommodation:
    multiplier = float(time_multiplier)
    days = int(due_date_extension_days)
    if not (MIN_MULTIPLIER <= multiplier <= MAX_MULTIPLIER):
        raise ValueError(
            f"Time multiplier must be between {MIN_MULTIPLIER} and {MAX_MULTIPLIER}."
        )
    if not (0 <= days <= MAX_EXTENSION_DAYS):
        raise ValueError(
            f"Due-date extension must be between 0 and {MAX_EXTENSION_DAYS} days."
        )
    record = get_record(db, user_id)
    if record is None:
        record = UserAccommodation(user_id=user_id)
        db.add(record)
    record.time_multiplier = multiplier
    record.due_date_extension_days = days
    record.notes = (notes or "").strip()[:500] or None
    record.updated_by_id = actor_id
    db.add(
        AccommodationEvent(
            user_id=user_id,
            actor_id=actor_id,
            action="updated",
            time_multiplier=multiplier,
            due_date_extension_days=days,
            reason=record.notes,
        )
    )
    db.commit()
    db.refresh(record)
    return record


def clear_accommodation(
    db, *, user_id: int, actor_id: int | None, reason: str = ""
) -> None:
    record = get_record(db, user_id)
    note = (reason or "").strip()[:500] or None
    db.add(
        AccommodationEvent(
            user_id=user_id,
            actor_id=actor_id,
            action="cleared",
            time_multiplier=1.0,
            due_date_extension_days=0,
            reason=note,
        )
    )
    if record is not None:
        db.delete(record)
    db.commit()


def serialize(record: UserAccommodation | None) -> dict:
    if record is None:
        return {
            "time_multiplier": 1.0,
            "due_date_extension_days": 0,
            "notes": None,
            "updated_at": None,
        }
    return {
        "time_multiplier": float(record.time_multiplier),
        "due_date_extension_days": int(record.due_date_extension_days or 0),
        "notes": record.notes,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }
