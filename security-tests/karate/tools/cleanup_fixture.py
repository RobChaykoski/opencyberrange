#!/usr/bin/env python3
"""Delete the disposable Karate identities recorded in the fixture JSON.

Reads the fixture on stdin:

    cat target/security-fixture.json \
      | docker exec -i ocr-backend python - < cleanup_fixture.py

User rows cascade to sessions, completions, and the other learner tables. The
script reports how many of the requested ids remain, so a partial cleanup is
visible rather than silent.
"""

from __future__ import annotations

import base64
import json
import sys

from app.database import SessionLocal
from sqlalchemy import bindparam, text


def main() -> int:
    try:
        if len(sys.argv) > 1:
            fixture = json.loads(base64.b64decode(sys.argv[1]).decode("utf-8"))
        else:
            fixture = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        print(f"invalid fixture JSON: {exc}", file=sys.stderr)
        return 2
    ids = [
        int(item["id"])
        for item in (fixture.get("users") or {}).values()
        if item.get("id") is not None
    ]
    if not ids:
        print(json.dumps({"requested": 0, "remaining": 0}))
        return 0
    with SessionLocal() as db:
        statement = text("DELETE FROM users WHERE id IN :ids").bindparams(
            bindparam("ids", expanding=True)
        )
        db.execute(statement, {"ids": ids})
        db.commit()
        remaining = db.execute(
            text("SELECT count(*) FROM users WHERE id IN :ids").bindparams(
                bindparam("ids", expanding=True)
            ),
            {"ids": ids},
        ).scalar_one()
    print(json.dumps({"requested": len(ids), "remaining": int(remaining)}))
    return 0 if int(remaining) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
