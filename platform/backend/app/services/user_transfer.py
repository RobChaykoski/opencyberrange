"""Portable user export/import shared by the admin UI.

The JSON shape matches ``scripts/user_transfer.py`` so an export produced by
either path can be imported by the other. Password hashes are carried
unchanged; MFA secrets, recovery codes, trusted devices, VPN peers, sessions,
and learning progress are deliberately excluded.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Integer, func
from sqlalchemy.orm import Session

from app.models import User
from app.services.erasure_ledger import is_erased

FORMAT = "opencyberrange-users"
VERSION = 1
ALLOWED_ROLES = {"student", "instructor", "admin"}

# Account/profile fields that are safe to move between installations. Keep this
# aligned with scripts/user_transfer.py EXPORT_FIELDS where they overlap.
EXPORT_FIELDS = (
    "username",
    "email",
    "student_id",
    "first_name",
    "last_name",
    "organization",
    "is_active",
    "is_admin",
    "role",
    "is_approved",
    "is_locked",
    "failed_attempts",
    "locked_at",
    "must_change_password",
    "created_at",
    "show_on_scoreboard",
    "scoreboard_name_mode",
    "is_minor",
    "certificates_public",
    "avatar_border_style",
    "avatar_border_color",
    "show_hidden_achievements",
    "equipped_title",
    "timezone",
    "notification_prefs",
    "login_notifications",
    "email_notifications",
    "email_consent_version",
    "email_consent_updated_at",
    "login_streak",
    "last_login_day",
    "survey_opt_in",
    "survey_opt_in_at",
    "survey_consent_version",
    "last_login_at",
    "last_login_ip",
    "data_exported_at",
)

# Fields accepted on import. ``created_at`` is applied to new accounts only so
# an update cannot rewrite the target installation's registration history.
IMPORT_FIELDS = tuple(
    field for field in EXPORT_FIELDS if field != "created_at"
) + ("avatar_data",)
MAX_WARNINGS = 100


def _json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime(value.year, value.month, value.day)
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    parsed = _parse_datetime(value)
    return parsed.date() if parsed else None


def _coerce(column, value: Any) -> Any:
    """Convert a JSON value to the type declared on the target column."""
    if value is None:
        return None
    column_type = column.type
    if isinstance(column_type, DateTime):
        return _parse_datetime(value)
    if isinstance(column_type, Date):
        return _parse_date(value)
    if isinstance(column_type, Boolean):
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)
    if isinstance(column_type, Integer):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    if isinstance(value, str):
        return value
    return str(value)


def export_users(db: Session, include_avatars: bool = False) -> dict:
    """Build the portable export payload for every account."""
    users = db.query(User).order_by(User.id).all()
    records = []
    for user in users:
        record = {
            field: _json_value(getattr(user, field))
            for field in EXPORT_FIELDS
            if hasattr(user, field)
        }
        record["password_hash"] = user.hashed_password
        if not record.get("role"):
            record["role"] = "admin" if user.is_admin else "student"
        if include_avatars:
            record["avatar_data"] = user.avatar_data
        records.append(record)

    return {
        "format": FORMAT,
        "version": VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user_count": len(records),
        "users": records,
    }


def _load_records(payload: Any) -> list:
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        if payload.get("format") not in (None, FORMAT):
            raise ValueError(f"unrecognised export format: {payload.get('format')!r}")
        if payload.get("version", VERSION) > VERSION:
            raise ValueError(
                f"export version {payload.get('version')} is newer than this importer"
            )
        records = payload.get("users")
    else:
        records = None

    if not isinstance(records, list):
        raise ValueError("export does not contain a users list")
    return records


def import_users(
    db: Session,
    payload: Any,
    *,
    update: bool = False,
    dry_run: bool = False,
    include_erased: bool = False,
    protect_user_id: int | None = None,
) -> dict:
    """Create or update accounts from a portable export payload.

    Each row is committed independently, matching the command-line utility, so
    one bad record does not discard the rest of the file. The caller is
    responsible for reporting the returned counts and warnings.
    """
    records = _load_records(payload)
    columns = {column.name: column for column in User.__table__.columns}
    created = updated = skipped = errors = 0
    warnings: list[str] = []
    warnings_truncated = False

    def warn(message: str) -> None:
        nonlocal warnings_truncated
        if len(warnings) < MAX_WARNINGS:
            warnings.append(message)
        else:
            warnings_truncated = True

    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            errors += 1
            warn(f"row {index}: not an object")
            continue

        username = str(record.get("username") or "").strip()
        email = str(record.get("email") or "").strip().lower()
        password_hash = record.get("password_hash") or record.get("hashed_password")

        if not include_erased and is_erased(username, email):
            skipped += 1
            warn(f"{username}: skipped (erased suppression ledger)")
            continue

        if not username or not email or not password_hash:
            errors += 1
            warn(f"row {index}: missing username, email, or password hash")
            continue

        role = str(
            record.get("role") or ("admin" if record.get("is_admin") else "student")
        ).lower()
        if role not in ALLOWED_ROLES:
            errors += 1
            warn(f"{username}: invalid role {role!r}")
            continue

        data: dict[str, Any] = {}
        for field in IMPORT_FIELDS:
            if field in record and field in columns:
                data[field] = _coerce(columns[field], record[field])

        # An empty student ID is the same as no student ID, and storing ""
        # would collide with the unique constraint on the second import.
        if data.get("student_id") == "":
            data["student_id"] = None

        # Never write an explicit NULL into a NOT NULL column that has a
        # default; a sparse or hand-edited export should fall back to it.
        for field, value in list(data.items()):
            column = columns.get(field)
            if value is None and column is not None and not column.nullable:
                data.pop(field)

        data["username"] = username
        data["email"] = email
        data["hashed_password"] = password_hash
        data["role"] = role
        data["is_admin"] = role == "admin"
        data.setdefault("is_active", True)
        data.setdefault("is_approved", True)
        data.setdefault("must_change_password", False)
        data.setdefault("is_locked", False)
        data.setdefault("failed_attempts", 0)

        created_at = None
        if record.get("created_at"):
            created_at = _parse_datetime(record["created_at"])
            if created_at is None:
                warn(f"{username}: could not parse created_at; using the current time")

        try:
            matches = (
                db.query(User)
                .filter(
                    (func.lower(User.username) == username.lower())
                    | (func.lower(User.email) == email)
                )
                .all()
            )
            exact = next(
                (
                    match
                    for match in matches
                    if str(match.username).lower() == username.lower()
                ),
                None,
            )
            if exact is None and matches:
                other = matches[0]
                skipped += 1
                warn(
                    f"{username}: email {email} already belongs to {other.username}"
                )
                continue

            if exact is not None:
                # Never let an import overwrite an administrator. The active
                # admin is the strongest case: replacing its password, email,
                # or role mid-session could lock the operator out of the
                # installation they are importing into. Other existing admins
                # are protected for the same reason; create or edit those
                # deliberately from the user panel instead.
                if protect_user_id is not None and exact.id == protect_user_id:
                    skipped += 1
                    warn(
                        f"{username}: skipped (the signed-in administrator is protected)"
                    )
                    continue
                if (exact.role or "").lower() == "admin" or exact.is_admin:
                    skipped += 1
                    warn(
                        f"{username}: skipped (existing administrator is protected)"
                    )
                    continue
                if not update:
                    skipped += 1
                    continue
                if dry_run:
                    updated += 1
                    continue
                for key, value in data.items():
                    if key != "created_at":
                        setattr(exact, key, value)
                db.commit()
                updated += 1
                continue

            student_id = data.get("student_id")
            if student_id:
                conflict = (
                    db.query(User).filter(User.student_id == student_id).first()
                )
                if conflict:
                    skipped += 1
                    warn(
                        f"{username}: student_id {student_id} already belongs to "
                        f"{conflict.username}"
                    )
                    continue

            if dry_run:
                created += 1
                continue

            if created_at is not None:
                data["created_at"] = created_at
            db.add(User(**data))
            db.commit()
            created += 1
        except Exception as exc:  # noqa: BLE001 - report per-row failures
            db.rollback()
            errors += 1
            warn(f"{username}: {exc}")

    if dry_run:
        db.rollback()

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "warnings": warnings,
        "warnings_truncated": warnings_truncated,
        "user_count": len(records),
    }
