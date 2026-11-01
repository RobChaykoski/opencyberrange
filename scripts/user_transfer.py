#!/usr/bin/env python3
"""Export and import OpenCyberRange users between installations.

The export intentionally contains password hashes, not plaintext passwords.
Treat the exported file as a secret: it contains account data and credential
material. MFA enrollments, recovery codes, trusted devices, VPN peer keys, and
completion history are not exported.

Run inside the backend container (psycopg2 is already installed):

    python /tmp/user_transfer.py export -o /tmp/users-export.json
    python /tmp/user_transfer.py import /tmp/users-export.json --dry-run
    python /tmp/user_transfer.py import /tmp/users-export.json
"""
import argparse
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

FORMAT = "opencyberrange-users"
VERSION = 1

# Common fields in the Lite/new schema. The exporter and importer both check
# information_schema, so a field is used only when the target table has it.
EXPORT_FIELDS = [
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
    "timezone",
    "notification_prefs",
    "login_notifications",
]

IMPORT_FIELDS = [f for f in EXPORT_FIELDS if f not in ("created_at",)]
ALLOWED_ROLES = {"student", "instructor", "admin"}


def fail(message: str, code: int = 1):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def connect(database_url: str):
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        return conn
    except Exception as exc:
        fail(f"could not connect to the database: {exc}")


def table_columns(conn) -> set:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = 'users'"
        )
        return {row[0] for row in cur.fetchall()}


def json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def export_users(args):
    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        fail("DATABASE_URL is not set; pass --database-url or run inside the backend")

    conn = connect(database_url)
    try:
        columns = table_columns(conn)
        if "username" not in columns or "email" not in columns or "hashed_password" not in columns:
            fail("the users table is missing username, email, or hashed_password")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users ORDER BY id")
            rows = cur.fetchall()

        users = []
        for row in rows:
            record = {}
            for field in EXPORT_FIELDS:
                if field in columns:
                    record[field] = json_value(row.get(field))

            # Export the tolerant field name, never the raw database column.
            record["password_hash"] = row.get("hashed_password")

            # The old schema may have is_admin but no role. Derive a role so the
            # new installation can preserve administrator access.
            if "role" not in record or not record.get("role"):
                record["role"] = "admin" if row.get("is_admin") else "student"

            if args.include_avatars and "avatar_data" in columns:
                record["avatar_data"] = row.get("avatar_data")

            users.append(record)

        payload = {
            "format": FORMAT,
            "version": VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user_count": len(users),
            "users": users,
        }

        output = Path(args.output).expanduser()
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        if os.name == "posix":
            os.chmod(output, stat.S_IRUSR | stat.S_IWUSR)

        print(f"exported {len(users)} user(s) to {output}")
        print("warning: this file contains password hashes and personal data; keep it private and delete it after import")
        missing = sum(1 for u in users if not u.get("password_hash"))
        if missing:
            print(f"warning: {missing} user(s) have no password hash")
    finally:
        conn.close()


def load_users(path: str):
    source = Path(path).expanduser()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {source}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {source}: {exc}")

    if isinstance(payload, list):
        users = payload
    elif isinstance(payload, dict):
        if payload.get("format") not in (None, FORMAT):
            fail(f"unrecognised export format: {payload.get('format')!r}")
        if payload.get("version", VERSION) > VERSION:
            fail(f"export version {payload.get('version')} is newer than this importer")
        users = payload.get("users")
    else:
        users = None

    if not isinstance(users, list):
        fail("export does not contain a users list")
    return users


def import_users(args):
    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        fail("DATABASE_URL is not set; pass --database-url or run inside the backend")

    records = load_users(args.input)
    conn = connect(database_url)
    created = updated = skipped = errors = 0
    warnings = []

    try:
        columns = table_columns(conn)
        if "username" not in columns or "email" not in columns or "hashed_password" not in columns:
            fail("the users table is missing username, email, or hashed_password")

        for index, record in enumerate(records, 1):
            if not isinstance(record, dict):
                errors += 1
                warnings.append(f"row {index}: not an object")
                continue

            username = str(record.get("username") or "").strip()
            email = str(record.get("email") or "").strip().lower()
            password_hash = record.get("password_hash") or record.get("hashed_password")
            if not username or not email or not password_hash:
                errors += 1
                warnings.append(f"row {index}: missing username, email, or password hash")
                continue

            role = str(record.get("role") or ("admin" if record.get("is_admin") else "student")).lower()
            if role not in ALLOWED_ROLES:
                errors += 1
                warnings.append(f"{username}: invalid role {role!r}")
                continue

            data = {}
            for field in IMPORT_FIELDS:
                if field in record and field in columns:
                    data[field] = record[field]

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

            for field in ("locked_at", "created_at"):
                if data.get(field):
                    parsed = parse_datetime(data[field])
                    if parsed is None:
                        warnings.append(f"{username}: could not parse {field}; leaving it empty")
                        data.pop(field, None)
                    else:
                        data[field] = parsed

            # Keep the target install's original creation date when updating an
            # existing account; the source date is only used for new accounts.
            update_data = {k: v for k, v in data.items() if k != "created_at"}
            insert_data = {k: v for k, v in data.items() if k in columns}
            update_data = {k: v for k, v in update_data.items() if k in columns}

            # Drop internal-only names that are not real columns.
            if "is_admin" not in columns:
                insert_data.pop("is_admin", None)
                update_data.pop("is_admin", None)

            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT id, username, email FROM users "
                        "WHERE lower(username) = lower(%s) OR lower(email) = lower(%s)",
                        (username, email),
                    )
                    matches = cur.fetchall()

                exact = next(
                    (m for m in matches if str(m["username"]).lower() == username.lower()),
                    None,
                )
                if exact is None and matches:
                    other = matches[0]
                    skipped += 1
                    warnings.append(
                        f"{username}: email {email} already belongs to {other['username']}"
                    )
                    continue

                if matches:
                    if not args.update:
                        skipped += 1
                        continue
                    if args.dry_run:
                        updated += 1
                        continue
                    assignments = ", ".join(f"{key} = %s" for key in update_data)
                    values = list(update_data.values()) + [exact["id"]]
                    with conn.cursor() as cur:
                        cur.execute(f"UPDATE users SET {assignments} WHERE id = %s", values)
                    conn.commit()
                    updated += 1
                else:
                    student_id = insert_data.get("student_id")
                    if student_id:
                        with conn.cursor() as cur:
                            cur.execute(
                                "SELECT username FROM users WHERE student_id = %s",
                                (student_id,),
                            )
                            conflict = cur.fetchone()
                        if conflict:
                            skipped += 1
                            warnings.append(
                                f"{username}: student_id {student_id} already belongs to {conflict[0]}"
                            )
                            continue

                    if args.dry_run:
                        created += 1
                        continue

                    keys = list(insert_data.keys())
                    placeholders = ", ".join("%s" for _ in keys)
                    with conn.cursor() as cur:
                        cur.execute(
                            f"INSERT INTO users ({', '.join(keys)}) VALUES ({placeholders})",
                            [insert_data[k] for k in keys],
                        )
                    conn.commit()
                    created += 1
            except Exception as exc:
                conn.rollback()
                errors += 1
                warnings.append(f"{username}: {exc}")
                continue

        if args.dry_run:
            conn.rollback()
        else:
            conn.commit()

        mode = "DRY RUN: " if args.dry_run else ""
        print(
            f"{mode}{created} created, {updated} updated, "
            f"{skipped} skipped, {errors} error(s)"
        )
        for warning in warnings[:50]:
            print(f"warning: {warning}")
        if len(warnings) > 50:
            print(f"warning: {len(warnings) - 50} more warning(s) not shown")
        if errors:
            raise SystemExit(1)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Export and import OpenCyberRange users")
    sub = parser.add_subparsers(dest="command", required=True)

    export_parser = sub.add_parser("export", help="Write a portable user export")
    export_parser.add_argument("-o", "--output", default="users-export.json")
    export_parser.add_argument("--database-url", help="Database URL; defaults to DATABASE_URL")
    export_parser.add_argument(
        "--include-avatars",
        action="store_true",
        help="Include profile avatar data (large; contains personal images)",
    )
    export_parser.set_defaults(func=export_users)

    import_parser = sub.add_parser("import", help="Read a portable user export")
    import_parser.add_argument("input")
    import_parser.add_argument("--database-url", help="Database URL; defaults to DATABASE_URL")
    import_parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing users by username instead of skipping them",
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report what would change without writing",
    )
    import_parser.set_defaults(func=import_users)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
