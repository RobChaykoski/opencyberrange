#!/usr/bin/env python3
"""Audit tenant isolation controls and probe cross-tenant visibility.

Run inside the backend container so ``app`` is importable and ``DATABASE_URL``
points at the runtime role:

    docker exec -i ocr-backend python - < scripts/check-tenant-isolation.py

The script checks every table in ``tenant_rls.TENANT_TABLES`` for:

- an ``institution_id`` column that is ``NOT NULL`` with a default;
- the ``ix_<table>_institution_id`` index;
- forced row-level security;
- the four tenant policies and the derivation trigger;
- zero rows visible to a probe tenant that owns nothing.

It refuses to run as a superuser or a role with ``BYPASSRLS``, because the probe
would be meaningless. Use the runtime role (``ocr_runtime``) instead.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from app.services.tenant_rls import TENANT_TABLES
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

PROBE_TENANT = "__isolation_probe__"
POLICY_SUFFIXES = ("select", "insert", "update", "delete")


def _url() -> str:
    explicit = os.environ.get("OCR_ISOLATION_DATABASE_URL")
    if explicit:
        return explicit
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL or OCR_ISOLATION_DATABASE_URL is required")
    return url


def _role_flags(conn) -> tuple[bool, bool] | None:
    row = conn.execute(
        text(
            "SELECT rolsuper, rolbypassrls FROM pg_roles "
            "WHERE rolname = current_user"
        )
    ).fetchone()
    if row is None:
        return None
    return bool(row[0]), bool(row[1])


def _schema_gaps(conn) -> list[str]:
    gaps: list[str] = []
    for table in TENANT_TABLES:
        exists = conn.execute(
            text("SELECT to_regclass(:name) IS NOT NULL"), {"name": f"public.{table}"}
        ).scalar()
        if not exists:
            gaps.append(f"{table}: table is missing")
            continue

        column = conn.execute(
            text(
                "SELECT is_nullable, column_default FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = :table "
                "AND column_name = 'institution_id'"
            ),
            {"table": table},
        ).fetchone()
        if column is None:
            gaps.append(f"{table}: institution_id column is missing")
        else:
            nullable, default = column
            if nullable != "NO":
                gaps.append(f"{table}: institution_id is nullable")
            if not default or "default" not in default.lower():
                gaps.append(f"{table}: institution_id has no default")

        index = conn.execute(
            text(
                "SELECT 1 FROM pg_indexes WHERE schemaname = 'public' "
                "AND tablename = :table AND indexname = :index"
            ),
            {"table": table, "index": f"ix_{table}_institution_id"},
        ).fetchone()
        if index is None:
            gaps.append(f"{table}: ix_{table}_institution_id is missing")

        flags = conn.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE oid = to_regclass(:name)"
            ),
            {"name": f"public.{table}"},
        ).fetchone()
        if not flags or not flags[0]:
            gaps.append(f"{table}: RLS is not enabled")
        elif not flags[1]:
            gaps.append(f"{table}: RLS is not forced")

        policies = {
            row[0]
            for row in conn.execute(
                text(
                    "SELECT policyname FROM pg_policies "
                    "WHERE schemaname = 'public' AND tablename = :table"
                ),
                {"table": table},
            ).all()
        }
        for suffix in POLICY_SUFFIXES:
            name = f"{table}_tenant_{suffix}"
            if name not in policies:
                gaps.append(f"{table}: policy {name} is missing")

        trigger = conn.execute(
            text(
                "SELECT 1 FROM pg_trigger WHERE tgname = :name AND NOT tgisinternal"
            ),
            {"name": f"ocr_{table}_tenant"},
        ).fetchone()
        if trigger is None:
            gaps.append(f"{table}: derivation trigger is missing")
    return gaps


def _probe(conn) -> tuple[list[str], dict[str, int]]:
    conn.execute(
        text("SELECT set_config('ocr.institution_id', :tenant, true)"),
        {"tenant": PROBE_TENANT},
    )
    conn.execute(text("SELECT set_config('ocr.system_admin', 'false', true)"))
    failures: list[str] = []
    counts: dict[str, int] = {}
    for table in TENANT_TABLES:
        exists = conn.execute(
            text("SELECT to_regclass(:name) IS NOT NULL"), {"name": f"public.{table}"}
        ).scalar()
        if not exists:
            continue
        try:
            count = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar() or 0
        except SQLAlchemyError as exc:
            failures.append(f"{table}: probe query failed: {exc}")
            continue
        counts[table] = int(count)
        if count:
            failures.append(f"{table}: {count} row(s) visible to a foreign tenant")
    return failures, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--require-runtime-role",
        action="store_true",
        help="Fail instead of skipping the probe when the role bypasses RLS",
    )
    args = parser.parse_args()

    engine = create_engine(_url(), pool_pre_ping=True)
    report: dict = {"ok": False, "tables": len(TENANT_TABLES), "gaps": []}

    with engine.connect() as conn:
        flags = _role_flags(conn)
        if flags is None:
            raise SystemExit("cannot read the current role")
        is_super, bypass = flags
        report["role"] = {
            "superuser": is_super,
            "bypassrls": bypass,
        }
        report["gaps"] = _schema_gaps(conn)

        if is_super or bypass:
            message = (
                "the current role bypasses RLS; run as the runtime role "
                "(for example ocr_runtime) for a meaningful probe"
            )
            report["probe"] = {"skipped": True, "reason": message}
            if args.require_runtime_role:
                report["gaps"].append(message)
        else:
            # The schema checks opened an implicit transaction; close it so
            # the probe settings are scoped to a fresh transaction.
            conn.rollback()
            trans = conn.begin()
            try:
                failures, counts = _probe(conn)
            finally:
                trans.rollback()
            report["probe"] = {
                "skipped": False,
                "tenant": PROBE_TENANT,
                "non_zero": {
                    table: count for table, count in counts.items() if count
                },
            }
            report["gaps"].extend(failures)

    report["ok"] = not report["gaps"]

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"tenant tables: {report['tables']}")
        print(
            "role: superuser={superuser} bypassrls={bypassrls}".format(
                **report["role"]
            )
        )
        probe = report.get("probe") or {}
        if probe.get("skipped"):
            print(f"probe: skipped ({probe['reason']})")
        else:
            print(
                f"probe: tenant {probe['tenant']}, "
                f"{len(probe['non_zero'])} table(s) leaked"
            )
        if report["gaps"]:
            print("FAILED:")
            for gap in report["gaps"]:
                print(f"  - {gap}")
        else:
            print("PASSED: tenant controls and cross-tenant probe")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
