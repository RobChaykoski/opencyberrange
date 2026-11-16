#!/usr/bin/env python3
"""Prove the runtime/migrator identities and tenant RLS on a live database.

Used by CI after ``db/bootstrap-db-roles.sql``. It creates a temporary
RLS-protected table, verifies that the runtime role sees only its tenant, cannot
create tables, and that the migrator role retains BYPASSRLS.
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError


def _engine(url: str):
    return create_engine(url, pool_pre_ping=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admin-url", required=True)
    parser.add_argument("--runtime-url", required=True)
    parser.add_argument("--migrator-url", required=True)
    args = parser.parse_args()

    admin = _engine(args.admin_url)
    runtime = _engine(args.runtime_url)
    migrator = _engine(args.migrator_url)

    try:
        with admin.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS role_probe"))
            conn.execute(
                text(
                    "CREATE TABLE role_probe ("
                    "id serial PRIMARY KEY, institution_id text NOT NULL)"
                )
            )
            conn.execute(text("ALTER TABLE role_probe ENABLE ROW LEVEL SECURITY"))
            conn.execute(text("ALTER TABLE role_probe FORCE ROW LEVEL SECURITY"))
            conn.execute(text("DROP POLICY IF EXISTS role_probe_tenant ON role_probe"))
            conn.execute(
                text(
                    "CREATE POLICY role_probe_tenant ON role_probe "
                    "USING (institution_id = NULLIF(current_setting("
                    "'ocr.institution_id', true), '')) "
                    "WITH CHECK (institution_id = NULLIF(current_setting("
                    "'ocr.institution_id', true), ''))"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO role_probe (institution_id) "
                    "VALUES ('tenant-a'), ('tenant-b')"
                )
            )
            conn.execute(text("ALTER TABLE role_probe OWNER TO ocr_migrator"))
            conn.execute(
                text(
                    "GRANT USAGE ON SCHEMA public TO ocr_runtime; "
                    "GRANT SELECT, INSERT ON role_probe TO ocr_runtime; "
                    "GRANT USAGE, SELECT ON SEQUENCE role_probe_id_seq TO ocr_runtime"
                )
            )

        with runtime.begin() as conn:
            identity = conn.execute(
                text(
                    "SELECT rolsuper, rolbypassrls FROM pg_roles "
                    "WHERE rolname = current_user"
                )
            ).fetchone()
            assert identity == (False, False), f"runtime identity is unsafe: {identity}"
            conn.execute(
                text(
                    "SELECT set_config('ocr.institution_id', 'tenant-a', true), "
                    "set_config('ocr.system_admin', 'false', true)"
                )
            )
            visible = conn.execute(
                text("SELECT institution_id, count(*) FROM role_probe GROUP BY 1")
            ).fetchall()
            assert visible == [("tenant-a", 1)], f"RLS leak: {visible}"
            try:
                conn.execute(text("CREATE TABLE runtime_ddl_should_fail (id int)"))
            except DBAPIError:
                pass
            else:
                raise AssertionError("runtime role can create tables")
            try:
                conn.execute(
                    text(
                        "INSERT INTO role_probe (institution_id) VALUES ('tenant-b')"
                    )
                )
            except DBAPIError:
                pass
            else:
                raise AssertionError("runtime role can insert into another tenant")

        with migrator.begin() as conn:
            identity = conn.execute(
                text(
                    "SELECT rolsuper, rolbypassrls FROM pg_roles "
                    "WHERE rolname = current_user"
                )
            ).fetchone()
            assert identity == (False, True), f"migrator identity is wrong: {identity}"
            count = conn.execute(text("SELECT count(*) FROM role_probe")).scalar()
            assert count == 2, f"migrator cannot see all tenants: {count}"

        print("PASS runtime=ocr_runtime no-superuser no-bypassrls")
        print("PASS tenant RLS and WITH CHECK")
        print("PASS runtime DDL denied")
        print("PASS migrator=ocr_migrator bypassrls")
        return 0
    finally:
        try:
            with admin.begin() as conn:
                conn.execute(text("DROP TABLE IF EXISTS role_probe"))
        except Exception:
            pass
        admin.dispose()
        runtime.dispose()
        migrator.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
