#!/usr/bin/env python3
"""Create disposable Karate test identities inside the backend container.

Run with the fixture id as the only argument:

    docker exec -i ocr-backend python - <run_id> < provision_fixture.py

Prints one JSON object to stdout. The accounts are active, approved, and
password-authenticated so the blackbox suite can log in through the real API.
Delete them with cleanup_fixture.py when the run finishes.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime

from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import User

PASSWORD = "Karate#Fixture2026!"  # Test-only credential; security-delta: allow
IDENTITIES = (
    ("student_a", "student"),
    ("student_b", "student"),
    ("instructor", "instructor"),
)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: provision_fixture.py <run_id>", file=sys.stderr)
        return 2
    run_id = "".join(ch for ch in sys.argv[1] if ch.isalnum())[:24]
    if not run_id:
        print("run_id must contain at least one alphanumeric character", file=sys.stderr)
        return 2
    now = datetime.now(UTC)
    password_hash = get_password_hash(PASSWORD)
    users: dict[str, dict] = {}
    with SessionLocal() as db:
        for suffix, role in IDENTITIES:
            username = f"karate_{run_id}_{suffix}"[:50]
            user = User(
                username=username,
                email=f"{username}@example.invalid",
                hashed_password=password_hash,
                is_active=True,
                is_approved=True,
                is_admin=False,
                is_locked=False,
                failed_attempts=0,
                role=role,
                institution_id="default",
                privacy_acknowledged_at=now,
                age_band="18_plus",
                is_minor=False,
                email_notifications=False,
                show_on_scoreboard=False,
                scoreboard_name_mode="anonymous",
                certificates_public=False,
            )
            db.add(user)
            db.flush()
            users[suffix] = {
                "id": user.id,
                "username": username,
                "email": user.email,
                "role": role,
            }
        db.commit()
    print(json.dumps({"run_id": run_id, "password": PASSWORD, "users": users}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
