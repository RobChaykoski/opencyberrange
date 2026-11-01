#!/usr/bin/env python3
"""Purge accounts that the erasure ledger says must stay deleted.

Use this after restoring a database dump or merging an old user export. The
dump may predate a deletion request; the live suppression ledger is the source
of truth. Run inside the backend container so the application models and
crypto settings are available:

    python /tmp/purge_erased_accounts.py --dry-run
    python /tmp/purge_erased_accounts.py

The script deliberately does not touch Docker or WireGuard; a restored dump
has no live lab sessions or peers. It refuses to delete instructors who still
own courses, exactly like the interactive erasure path.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-apply erasure after a database restore or user import"
    )
    parser.add_argument(
        "--ledger",
        default=os.environ.get("ERASURE_LEDGER_PATH", "/workbook/erasure-ledger.jsonl"),
        help="Path to the suppression ledger",
    )
    parser.add_argument(
        "--ledger-key",
        default=os.environ.get("ERASURE_LEDGER_KEY") or os.environ.get("JWT_SECRET"),
        help="Key used to hash ledger identifiers",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Database URL; defaults to DATABASE_URL",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching accounts without deleting anything",
    )
    args = parser.parse_args()

    if not args.database_url:
        print("error: DATABASE_URL is not set", file=sys.stderr)
        return 2
    if not Path(args.ledger).expanduser().exists():
        print(f"error: ledger not found: {args.ledger}", file=sys.stderr)
        return 2

    # Import lazily so --help works outside the backend image.
    try:
        from app.database import SessionLocal
        from app.models import User
        from app.services.erasure import ErasureBlocked, erase_user
        from app.services.erasure_ledger import identifier_hashes, load_erased_hashes
    except Exception as exc:
        print(
            "error: this script must run inside the OpenCyberRange backend "
            f"container (import failed: {exc})",
            file=sys.stderr,
        )
        return 2

    erased = load_erased_hashes(args.ledger)
    if not erased:
        print("No suppression entries found; nothing to purge.")
        return 0

    db = SessionLocal()
    matches = []
    try:
        for user in db.query(User).order_by(User.id).all():
            hashes = identifier_hashes(user.username, user.email, args.ledger_key)
            if hashes & erased:
                matches.append((user.id, user.username, user.email, user.role))

        if not matches:
            print("No restored accounts match the suppression ledger.")
            return 0

        print(f"{len(matches)} account(s) match the suppression ledger:")
        for _user_id, username, email, role in matches:
            print(f"  {username} <{email}> ({role})")

        if args.dry_run:
            print("Dry run: no changes made.")
            return 0

        failures = 0
        for user_id, username, _email, _role in matches:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                continue
            try:
                result = erase_user(
                    db,
                    user,
                    actor="restore-purge",
                    external_cleanup=False,
                    write_ledger=False,
                )
                print(f"  purged {username}: {result.deleted}")
            except ErasureBlocked as exc:
                failures += 1
                print(f"  BLOCKED {username}: {exc.message}", file=sys.stderr)
            except Exception as exc:
                failures += 1
                print(f"  FAILED {username}: {exc}", file=sys.stderr)

        return 1 if failures else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
