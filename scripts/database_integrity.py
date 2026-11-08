#!/usr/bin/env python3
"""Read-only database integrity and quality checks.

Run inside the backend container so ``DATABASE_URL`` and ``psycopg`` are
available:

    docker exec -i ocr-backend python - --checksum
    docker exec -i ocr-backend python - --quality
    docker exec -i ocr-backend python - --write-manifest /tmp/db.json
    docker exec -i ocr-backend python - --verify /tmp/db.json

The tool never writes to the platform schema. ``--write-manifest`` writes only
the requested manifest file. The manifest is a point-in-time evidence artefact;
the database fingerprint is the stable identifier for that snapshot.

Set ``DB_INTEGRITY_KEY`` to sign the manifest with HMAC-SHA256. Without the key,
``--write-manifest`` refuses unless ``--allow-unsigned`` is passed.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

try:
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row
except Exception as exc:  # pragma: no cover - only when run outside the image
    raise SystemExit(f"psycopg is required: {exc}")

CRITICAL_TABLES = [
    "users",
    "courses",
    "course_enrollments",
    "course_lab_assignments",
    "labs",
    "levels",
    "tracks",
    "lab_completions",
    "lab_sessions",
    "achievements",
    "achievement_celebrations",
    "exercise_quiz_attempts",
    "exercise_quiz_feedback",
    "course_feedback",
    "survey_responses",
    "platform_settings",
]

JSON_COLUMNS = {
    "labs": ["hints", "objectives", "topology_nodes", "tools", "hostnames"],
    "survey_responses": ["answers"],
    "exercise_quiz_attempts": ["question_keys", "answers"],
    "platform_settings": [],
}

ENUM_CHECKS = [
    ("users", "role", ["student", "instructor", "admin"]),
    ("labs", "difficulty", ["beginner", "intermediate", "advanced", "expert"]),
    ("course_feedback", "direction", ["student_course", "instructor_student"]),
    ("lab_sessions", "status", ["running", "stopped", "expired", "error", "starting", "active"]),
]

NULL_CHECKS = [
    ("users", "username", "critical"),
    ("users", "email", "warning"),
    ("users", "role", "critical"),
    ("courses", "code", "critical"),
    ("courses", "name", "critical"),
    ("courses", "instructor_id", "critical"),
    ("courses", "start_date", "warning"),
    ("courses", "end_date", "warning"),
    ("course_enrollments", "enrolled_at", "warning"),
    ("course_lab_assignments", "assigned_at", "warning"),
    ("labs", "level_id", "critical"),
    ("labs", "category", "warning"),
    ("labs", "difficulty", "warning"),
    ("labs", "duration_minutes", "warning"),
    ("lab_completions", "completed_at", "critical"),
    ("lab_sessions", "started_at", "warning"),
    ("achievements", "awarded_at", "warning"),
    ("platform_settings", "value", "warning"),
]

DEFAULT_SETTING_KEYS = [
    "default_session_hours",
    "max_session_hours",
    "container_cpu_limit",
    "container_memory_limit",
    "jwt_expiration_hours",
    "max_failed_attempts",
    "lockout_duration_minutes",
    "require_approval",
    "enable_api_docs",
]


def connect():
    url = os.environ.get("DATABASE_URL") or os.environ.get("TEST_DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required")
    return psycopg.connect(url, row_factory=dict_row)


def table_exists(conn, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
        (table,),
    ).fetchone()
    return row is not None


def count_sql(conn, sql_text: str, params: tuple = ()) -> int:
    row = conn.execute(sql_text, params).fetchone()
    return int(next(iter(row.values()))) if row else 0


def table_checksum(conn, table: str) -> dict:
    if not table_exists(conn, table):
        return {"present": False, "rows": 0, "sha256": None}
    ident = sql.Identifier(table)
    # Every critical table has an integer id primary key. Fall back to all
    # columns only if a future table does not.
    row = conn.execute(
        sql.SQL(
            "SELECT count(*) AS rows, "
            "encode(digest(coalesce(string_agg(row_to_json(t)::text, E'\\n' ORDER BY t.id), ''), 'sha256'), 'hex') AS sha256 "
            "FROM public.{} t"
        ).format(ident)
    ).fetchone()
    return {"present": True, "rows": int(row["rows"]), "sha256": row["sha256"]}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign_manifest(manifest: dict, key: str) -> dict:
    payload = {k: v for k, v in manifest.items() if k not in {"signature", "key_id"}}
    signature = hmac.new(
        key.encode("utf-8"), canonical_json(payload).encode("utf-8"), hashlib.sha256
    ).hexdigest()
    signed = dict(manifest)
    signed["signature"] = signature
    signed["key_id"] = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return signed


def build_manifest(conn) -> dict:
    tables = {table: table_checksum(conn, table) for table in CRITICAL_TABLES}
    fingerprint = hashlib.sha256(canonical_json(tables).encode("utf-8")).hexdigest()
    try:
        from app.version import APP_VERSION  # type: ignore

        release = APP_VERSION
    except Exception:
        release = os.environ.get("OCR_RELEASE", "unknown")
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "database": os.environ.get("PGDATABASE") or "labdb",
        "release": release,
        "tables": tables,
        "fingerprint": fingerprint,
    }


def write_manifest(conn, path: str, allow_unsigned: bool) -> int:
    manifest = build_manifest(conn)
    key = os.environ.get("DB_INTEGRITY_KEY", "")
    if key:
        manifest = sign_manifest(manifest, key)
    elif not allow_unsigned:
        raise SystemExit(
            "DB_INTEGRITY_KEY is not set; use --allow-unsigned for a checksum-only manifest"
        )
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({
        "written": path,
        "fingerprint": manifest["fingerprint"],
        "signed": bool(key),
    }, indent=2))
    return 0


def verify_manifest(conn, path: str) -> int:
    with open(path, encoding="utf-8") as handle:
        expected = json.load(handle)
    key = os.environ.get("DB_INTEGRITY_KEY", "")
    errors: list[str] = []
    if expected.get("signature"):
        if not key:
            errors.append("manifest is signed but DB_INTEGRITY_KEY is not set")
        else:
            payload = {k: v for k, v in expected.items() if k not in {"signature", "key_id"}}
            want = hmac.new(
                key.encode("utf-8"),
                canonical_json(payload).encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(want, expected["signature"]):
                errors.append("manifest signature does not match")
    else:
        print("WARN: manifest is unsigned; comparing checksums only", file=sys.stderr)

    current = build_manifest(conn)
    if expected.get("fingerprint") != current["fingerprint"]:
        errors.append(
            f"database fingerprint changed: {expected.get('fingerprint')} -> {current['fingerprint']}"
        )
    for table, expected_row in sorted((expected.get("tables") or {}).items()):
        current_row = current["tables"].get(table)
        if current_row is None:
            errors.append(f"table missing from current database: {table}")
            continue
        if expected_row.get("rows") != current_row.get("rows"):
            errors.append(
                f"{table}: row count {expected_row.get('rows')} -> {current_row.get('rows')}"
            )
        if expected_row.get("sha256") != current_row.get("sha256"):
            errors.append(f"{table}: checksum changed")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} integrity difference(s)")
        return 1
    print(f"OK: database matches manifest {expected.get('fingerprint')}")
    return 0


def add_check(results: list[dict], check_id: str, severity: str, count: int, detail: str, sample=None):
    results.append({
        "id": check_id,
        "severity": severity,
        "count": int(count),
        "detail": detail,
        "sample": sample or [],
    })


def orphan_checks(conn, results: list[dict]):
    fks = conn.execute(
        """
        SELECT
            tc.table_name AS child_table,
            kcu.column_name AS child_column,
            ccu.table_name AS parent_table,
            ccu.column_name AS parent_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name
         AND kcu.table_schema = tc.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
        ORDER BY tc.table_name, kcu.column_name
        """,
    ).fetchall()
    seen = set()
    for fk in fks:
        key = (fk["child_table"], fk["child_column"], fk["parent_table"])
        if key in seen:
            continue
        seen.add(key)
        child = sql.Identifier(fk["child_table"])
        child_col = sql.Identifier(fk["child_column"])
        parent = sql.Identifier(fk["parent_table"])
        parent_col = sql.Identifier(fk["parent_column"])
        query = sql.SQL(
            "SELECT count(*) AS n FROM public.{child} c "
            "LEFT JOIN public.{parent} p ON c.{child_col} = p.{parent_col} "
            "WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL"
        ).format(child=child, parent=parent, child_col=child_col, parent_col=parent_col)
        n = count_sql(conn, query.as_string(conn))
        if n:
            add_check(
                results,
                f"orphan:{fk['child_table']}.{fk['child_column']}->{fk['parent_table']}",
                "critical",
                n,
                f"{n} orphaned {fk['child_table']}.{fk['child_column']} row(s)",
            )


def duplicate_checks(conn, results: list[dict]):
    checks = [
        ("users", ["username"]),
        ("users", ["email"]),
        ("labs", ["slug"]),
        ("course_enrollments", ["course_id", "user_id"]),
        ("course_lab_assignments", ["course_id", "lab_id"]),
        ("lab_completions", ["user_id", "lab_id"]),
        ("achievements", ["user_id", "course_id", "achievement_type", "lab_id"]),
        ("achievement_celebrations", ["achievement_id", "user_id"]),
        ("exercise_quiz_feedback", ["user_id", "lab_id"]),
        ("course_feedback", ["course_id", "author_id", "direction", "subject_user_id"]),
        ("platform_settings", ["key"]),
    ]
    for table, columns in checks:
        if not table_exists(conn, table):
            continue
        ident = sql.Identifier(table)
        cols = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
        query = sql.SQL(
            "SELECT count(*) AS n FROM ("
            "SELECT {cols} FROM public.{table} GROUP BY {cols} HAVING count(*) > 1"
            ") d"
        ).format(cols=cols, table=ident)
        n = count_sql(conn, query.as_string(conn))
        if n:
            add_check(
                results,
                f"duplicate:{table}({','.join(columns)})",
                "critical",
                n,
                f"{n} duplicate key group(s) in {table}",
            )


def value_checks(conn, results: list[dict]):
    for table, column, allowed in ENUM_CHECKS:
        if not table_exists(conn, table):
            continue
        ident = sql.Identifier(table)
        col = sql.Identifier(column)
        placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in allowed)
        query = sql.SQL(
            "SELECT count(*) AS n FROM public.{table} WHERE {col} IS NOT NULL AND {col} NOT IN ({allowed})"
        ).format(table=ident, col=col, allowed=placeholders)
        n = count_sql(conn, query.as_string(conn), tuple(allowed))
        if n:
            add_check(
                results,
                f"invalid:{table}.{column}",
                "critical",
                n,
                f"{n} row(s) have an unexpected {table}.{column}",
            )

    for table, column, severity in NULL_CHECKS:
        if not table_exists(conn, table):
            continue
        ident = sql.Identifier(table)
        col = sql.Identifier(column)
        query = sql.SQL(
            "SELECT count(*) AS n FROM public.{table} WHERE {col} IS NULL"
        ).format(table=ident, col=col)
        n = count_sql(conn, query.as_string(conn))
        if n:
            add_check(
                results,
                f"null:{table}.{column}",
                severity,
                n,
                f"{n} row(s) have a null {table}.{column}",
            )


def business_checks(conn, results: list[dict]):
    checks = [
        (
            "course_dates",
            "critical",
            "SELECT count(*) AS n FROM courses WHERE start_date IS NOT NULL AND end_date IS NOT NULL AND start_date > end_date",
            "course start_date is after end_date",
        ),
        (
            "completion_negative",
            "critical",
            "SELECT count(*) AS n FROM lab_completions WHERE attempts < 0 OR hints_used < 0 OR time_spent_minutes < 0",
            "negative attempts, hints, or time on a completion",
        ),
        (
            "completion_flag_empty",
            "critical",
            "SELECT count(*) AS n FROM lab_completions WHERE (flag_submitted IS NULL OR btrim(flag_submitted) = '') AND NOT (attempts = 0 AND hints_used = 0 AND started_at IS NOT NULL)",
            "completion without a submitted flag and not a hint placeholder",
        ),
        (
            "placeholder_completion",
            "info",
            "SELECT count(*) AS n FROM lab_completions WHERE (flag_submitted IS NULL OR btrim(flag_submitted) = '') AND attempts = 0 AND hints_used = 0 AND started_at IS NOT NULL",
            "hint placeholder completion (intentional, not a solved exercise)",
        ),
        (
            "quiz_score_range",
            "critical",
            "SELECT count(*) AS n FROM exercise_quiz_attempts WHERE score IS NOT NULL AND (score < 0 OR score > 100)",
            "quiz score outside 0-100",
        ),
        (
            "quiz_correct_total",
            "critical",
            "SELECT count(*) AS n FROM exercise_quiz_attempts WHERE correct IS NOT NULL AND total IS NOT NULL AND (correct < 0 OR correct > total)",
            "quiz correct count exceeds total",
        ),
        (
            "quiz_total_zero",
            "warning",
            "SELECT count(*) AS n FROM exercise_quiz_attempts WHERE completed_at IS NOT NULL AND (total IS NULL OR total <= 0)",
            "submitted quiz attempt with no questions",
        ),
        (
            "feedback_rating_range",
            "critical",
            "SELECT count(*) AS n FROM course_feedback WHERE (clarity IS NOT NULL AND (clarity < 1 OR clarity > 5)) OR (challenge IS NOT NULL AND (challenge < 1 OR challenge > 5)) OR (engagement IS NOT NULL AND (engagement < 1 OR engagement > 5)) OR (confidence IS NOT NULL AND (confidence < 1 OR confidence > 5))",
            "course feedback rating outside 1-5",
        ),
        (
            "quiz_feedback_rating_range",
            "critical",
            "SELECT count(*) AS n FROM exercise_quiz_feedback WHERE (satisfaction IS NOT NULL AND (satisfaction < 1 OR satisfaction > 5)) OR (relevance IS NOT NULL AND (relevance < 1 OR relevance > 5)) OR (usefulness IS NOT NULL AND (usefulness < 1 OR usefulness > 5)) OR (ease_of_use IS NOT NULL AND (ease_of_use < 1 OR ease_of_use > 5))",
            "quiz feedback rating outside 1-5",
        ),
        (
            "instructor_feedback_no_subject",
            "critical",
            "SELECT count(*) AS n FROM course_feedback WHERE direction = 'instructor_student' AND subject_user_id IS NULL",
            "instructor coaching note without a student (deleted account or bad write)",
        ),
        (
            "password_hash_format",
            "critical",
            "SELECT count(*) AS n FROM users WHERE hashed_password IS NULL OR btrim(hashed_password) = '' OR (left(hashed_password, 10) <> '$argon2id$' AND left(hashed_password, 4) NOT IN ('$2a$', '$2b$', '$2y$'))",
            "password hash is missing or is not a one-way Argon2id/bcrypt hash",
        ),
        (
            "plaintext_password_column",
            "critical",
            "SELECT count(*) AS n FROM information_schema.columns WHERE table_schema='public' AND table_name='users' AND column_name IN ('password', 'plaintext_password', 'encrypted_password')",
            "a users table column suggests plaintext or reversible password storage",
        ),
        (
            "deleted_lab_creator",
            "info",
            "SELECT count(*) AS n FROM labs WHERE created_by IS NULL",
            "lab has no creator (system import or deleted account)",
        ),
        (
            "deleted_survey_creator",
            "info",
            "SELECT count(*) AS n FROM surveys WHERE created_by IS NULL",
            "survey has no creator (system import or deleted account)",
        ),
        (
            "deleted_competition_creator",
            "info",
            "SELECT count(*) AS n FROM competitions WHERE created_by IS NULL",
            "competition has no creator (system import or deleted account)",
        ),
        (
            "activity_without_actor",
            "info",
            "SELECT count(*) AS n FROM activity_events WHERE actor_id IS NULL",
            "activity event with no actor (system action or deleted account)",
        ),
        (
            "student_feedback_with_subject",
            "warning",
            "SELECT count(*) AS n FROM course_feedback WHERE direction = 'student_course' AND subject_user_id IS NOT NULL",
            "student check-in carries a subject",
        ),
        (
            "future_timestamps",
            "warning",
            "SELECT count(*) AS n FROM lab_completions WHERE completed_at > now() + interval '1 day'",
            "completion timestamp more than one day in the future",
        ),
        (
            "course_no_assignments",
            "warning",
            "SELECT count(*) AS n FROM courses c WHERE c.is_active = true AND NOT EXISTS (SELECT 1 FROM course_lab_assignments a WHERE a.course_id = c.id)",
            "active course with no assigned exercises",
        ),
        (
            "course_no_enrollments",
            "warning",
            "SELECT count(*) AS n FROM courses c WHERE c.is_active = true AND NOT EXISTS (SELECT 1 FROM course_enrollments e WHERE e.course_id = c.id)",
            "active course with no enrolled students",
        ),
        (
            "archived_course_enrollments",
            "warning",
            "SELECT count(*) AS n FROM course_enrollments e JOIN courses c ON c.id = e.course_id WHERE c.is_archived = true",
            "enrollment in an archived course",
        ),
        (
            "completion_without_session",
            "info",
            "SELECT count(*) AS n FROM lab_completions c WHERE c.flag_submitted IS NOT NULL AND btrim(c.flag_submitted) <> '' AND NOT EXISTS (SELECT 1 FROM lab_sessions s WHERE s.user_id = c.user_id AND s.lab_id = c.lab_id AND s.is_diagnostic = false)",
            "completion without a matching non-diagnostic session (known data gap)",
        ),
        (
            "active_lab_without_level",
            "critical",
            "SELECT count(*) AS n FROM labs WHERE is_active = true AND level_id IS NULL",
            "active lab without a level",
        ),
        (
            "lab_without_flag",
            "warning",
            "SELECT count(*) AS n FROM labs WHERE is_active = true AND (flag_hash IS NULL OR btrim(flag_hash) = '')",
            "active lab without a flag hash",
        ),
    ]
    for check_id, severity, sql_text, detail in checks:
        try:
            n = count_sql(conn, sql_text)
        except Exception as exc:
            add_check(results, check_id, "warning", 0, f"check could not run: {exc}")
            continue
        if n:
            add_check(results, check_id, severity, n, f"{n}: {detail}")


def json_checks(conn, results: list[dict]):
    for table, columns in JSON_COLUMNS.items():
        if not table_exists(conn, table) or not columns:
            continue
        for column in columns:
            ident = sql.Identifier(table)
            col = sql.Identifier(column)
            query = sql.SQL(
                "SELECT id, {col} AS value FROM public.{table} WHERE {col} IS NOT NULL AND btrim({col}) <> ''"
            ).format(table=ident, col=col)
            rows = conn.execute(query.as_string(conn)).fetchall()
            invalid = []
            for row in rows:
                try:
                    json.loads(row["value"])
                except (TypeError, ValueError):
                    invalid.append(row["id"])
            if invalid:
                add_check(
                    results,
                    f"invalid_json:{table}.{column}",
                    "warning",
                    len(invalid),
                    f"{len(invalid)} row(s) contain invalid JSON in {table}.{column}",
                    invalid[:5],
                )


def settings_checks(conn, results: list[dict]):
    if not table_exists(conn, "platform_settings"):
        add_check(results, "missing_table:platform_settings", "critical", 1, "platform_settings table is missing")
        return
    rows = conn.execute("SELECT key FROM platform_settings").fetchall()
    present = {row["key"] for row in rows}
    missing = [key for key in DEFAULT_SETTING_KEYS if key not in present]
    if missing:
        add_check(
            results,
            "missing_settings",
            "warning",
            len(missing),
            f"missing platform settings: {', '.join(missing)}",
            missing,
        )


def run_quality(conn, as_json: bool) -> int:
    results: list[dict] = []
    orphan_checks(conn, results)
    duplicate_checks(conn, results)
    value_checks(conn, results)
    business_checks(conn, results)
    json_checks(conn, results)
    settings_checks(conn, results)

    results.sort(key=lambda row: ({"critical": 0, "warning": 1, "info": 2}.get(row["severity"], 3), row["id"]))
    critical = sum(1 for row in results if row["severity"] == "critical")
    warning = sum(1 for row in results if row["severity"] == "warning")
    info = sum(1 for row in results if row["severity"] == "info")
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "critical": critical,
        "warning": warning,
        "info": info,
        "findings": results,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Database quality: {critical} critical, {warning} warning, {info} info")
        for row in results:
            print(f"[{row['severity'].upper():8}] {row['id']}: {row['detail']}")
        if not results:
            print("No quality findings.")
    return 1 if critical else 0


def verify_ledger(conn, as_json: bool) -> int:
    if not table_exists(conn, "data_integrity_ledger"):
        print("Ledger: not installed")
        return 1
    rows = conn.execute(
        "SELECT id, occurred_at::text AS occurred_at_text, table_name, row_pk, "
        "operation, row_hash, actor_type, actor_id, request_id, prev_hash, entry_hash "
        "FROM data_integrity_ledger ORDER BY id"
    ).fetchall()
    prev = "0" * 64
    errors: list[str] = []
    unattributed: dict[str, int] = {}
    for row in rows:
        if row["prev_hash"] != prev:
            errors.append(f"ledger {row['id']}: prev_hash does not match the previous entry")
        material = (
            row["prev_hash"]
            + row["table_name"]
            + row["row_pk"]
            + row["operation"]
            + row["row_hash"]
            + row["actor_type"]
            + ("" if row["actor_id"] is None else str(row["actor_id"]))
            + (row["request_id"] or "")
            + row["occurred_at_text"]
        )
        expected = hashlib.sha256(material.encode("utf-8")).hexdigest()
        if expected != row["entry_hash"]:
            errors.append(f"ledger {row['id']}: entry_hash does not match its fields")
        if row["actor_type"] == "unattributed":
            key = f"{row['table_name']}.{row['operation']}"
            unattributed[key] = unattributed.get(key, 0) + 1
        prev = row["entry_hash"]

    payload = {
        "entries": len(rows),
        "chain_ok": not errors,
        "unattributed": unattributed,
        "errors": errors,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Ledger: {len(rows)} entries; chain {'OK' if not errors else 'BROKEN'}")
        for error in errors:
            print(f"ERROR: {error}")
        if unattributed:
            print("WARN: unattributed writes (manual or uninstrumented):")
            for key, count in sorted(unattributed.items()):
                print(f"  {key}: {count}")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checksum", action="store_true", help="print table checksums and the database fingerprint")
    parser.add_argument("--quality", action="store_true", help="run data-quality checks")
    parser.add_argument("--write-manifest", metavar="PATH", help="write a signed or unsigned manifest")
    parser.add_argument("--verify", metavar="PATH", help="verify the database against a manifest")
    parser.add_argument("--ledger", action="store_true", help="verify the append-only change ledger")
    parser.add_argument("--allow-unsigned", action="store_true", help="write a manifest without DB_INTEGRITY_KEY")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if not any((args.checksum, args.quality, args.write_manifest, args.verify, args.ledger)):
        parser.error("choose --checksum, --quality, --write-manifest, --verify, or --ledger")

    with connect() as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        if args.checksum:
            print(json.dumps(build_manifest(conn), indent=2, sort_keys=True))
        if args.quality:
            return run_quality(conn, args.json)
        if args.ledger:
            return verify_ledger(conn, args.json)
        if args.write_manifest:
            return write_manifest(conn, args.write_manifest, args.allow_unsigned)
        if args.verify:
            return verify_manifest(conn, args.verify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
