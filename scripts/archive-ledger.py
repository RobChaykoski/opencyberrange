#!/usr/bin/env python3
"""Archive and optionally prune the append-only integrity ledger in chunks.

Run inside the backend container so ``DATABASE_URL`` and ``psycopg`` are
available. The default is a dry run that exports and hashes the chunks; deletion
requires both ``--apply`` and ``--confirm-delete``.

Examples:

    docker exec -w /app -e PYTHONPATH=/app ocr-backend \
        python /tmp/archive-ledger.py --before 2024-01-01 --chunk-days 30

    docker exec -w /app -e PYTHONPATH=/app ocr-backend \
        python /tmp/archive-ledger.py --before 2024-01-01 --apply --confirm-delete

The manifest records each chunk's row range, row count, first/last entry hash,
and the SHA-256 of the exported JSONL. Sign it with ``DB_INTEGRITY_KEY`` to keep
the archive tamper-evident. The first retained ledger row becomes the new chain
boundary; its ``prev_hash`` is recorded in the manifest.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import hmac
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"psycopg is required: {exc}")

COLUMNS = (
    "id", "occurred_at", "table_name", "row_pk", "operation", "row_hash",
    "actor_type", "actor_id", "request_id", "prev_hash", "entry_hash",
)


def connect():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required")
    return psycopg.connect(url, row_factory=dict_row)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sign_manifest(manifest: dict) -> str | None:
    key = os.environ.get("DB_INTEGRITY_KEY", "").strip()
    if not key:
        return None
    material = json.dumps(manifest, sort_keys=True, separators=(",", ":"), default=str)
    return hmac.new(key.encode(), material.encode(), hashlib.sha256).hexdigest()


def ledger_triggers(conn) -> list[str]:
    rows = conn.execute(
        "select tgname from pg_trigger "
        "where tgrelid = 'data_integrity_ledger'::regclass and not tgisinternal"
    ).fetchall()
    return [row["tgname"] for row in rows]


def archive(args) -> int:
    before = date.fromisoformat(args.before)
    keep_cutoff = datetime.now(timezone.utc).date() - timedelta(days=args.keep_days)
    if before > keep_cutoff:
        raise SystemExit(
            f"refusing to archive after {keep_cutoff}: keep at least {args.keep_days} days"
        )

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    chunk_delta = timedelta(days=args.chunk_days)

    with connect() as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        first = conn.execute(
            "select min(occurred_at) as start from data_integrity_ledger"
        ).fetchone()["start"]
        if first is None:
            print("ledger is empty; nothing to archive")
            return 0

        total = conn.execute(
            "select count(*) as n from data_integrity_ledger where occurred_at < %s",
            (before,),
        ).fetchone()["n"]
        if total == 0:
            print(f"no rows before {before}")
            return 0

        chunks = []
        start = first.date()
        while start < before:
            end = min(start + chunk_delta, before)
            rows = conn.execute(
                "select * from data_integrity_ledger "
                "where occurred_at >= %s and occurred_at < %s order by id",
                (start, end),
            ).fetchall()
            if rows:
                filename = f"ledger-{start.isoformat()}_{end.isoformat()}.jsonl.gz"
                path = out_dir / filename
                with gzip.open(path, "wt", encoding="utf-8") as handle:
                    for row in rows:
                        handle.write(json.dumps(row, default=str, sort_keys=True) + "\n")
                chunks.append({
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "rows": len(rows),
                    "first_id": rows[0]["id"],
                    "last_id": rows[-1]["id"],
                    "first_entry_hash": rows[0]["entry_hash"],
                    "last_entry_hash": rows[-1]["entry_hash"],
                    "file": filename,
                    "sha256": sha256_file(path),
                })
            start = end

        boundary = conn.execute(
            "select prev_hash, entry_hash, id, occurred_at from data_integrity_ledger "
            "where occurred_at >= %s order by id limit 1",
            (before,),
        ).fetchone()

        manifest = {
            "schema": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "before": before.isoformat(),
            "chunk_days": args.chunk_days,
            "keep_days": args.keep_days,
            "total_rows": total,
            "chunks": chunks,
            "new_chain_boundary": {
                "first_retained_id": boundary["id"] if boundary else None,
                "prev_hash": boundary["prev_hash"] if boundary else None,
                "entry_hash": boundary["entry_hash"] if boundary else None,
                "occurred_at": boundary["occurred_at"].isoformat() if boundary else None,
            },
        }
        manifest["signature"] = sign_manifest(manifest)
        manifest_path = out_dir / f"ledger-archive-{before.isoformat()}.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
        print(f"exported {total} rows in {len(chunks)} chunk(s) to {out_dir}")
        print(f"manifest: {manifest_path}")
        if not manifest.get("signature"):
            print("warning: DB_INTEGRITY_KEY is not set; manifest is unsigned")

        if not args.apply:
            print("dry run: no rows deleted. Add --apply --confirm-delete to prune.")
            return 0
        if not args.confirm_delete:
            print("refusing to delete without --confirm-delete")
            return 2

        triggers = ledger_triggers(conn)
        conn.commit()
        conn.execute("BEGIN")
        try:
            for name in triggers:
                conn.execute(f'ALTER TABLE data_integrity_ledger DISABLE TRIGGER "{name}"')
            deleted = 0
            for chunk in chunks:
                result = conn.execute(
                    "delete from data_integrity_ledger "
                    "where occurred_at >= %s and occurred_at < %s",
                    (chunk["start"], chunk["end"]),
                )
                deleted += result.rowcount
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            for name in triggers:
                conn.execute(f'ALTER TABLE data_integrity_ledger ENABLE TRIGGER "{name}"')
            conn.commit()
        conn.execute("VACUUM (ANALYZE) data_integrity_ledger")
        print(f"deleted {deleted} rows; chain boundary recorded in the manifest")
        return 0


def verify(args) -> int:
    manifest_path = Path(args.verify)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("signature")
    if expected:
        actual = sign_manifest({k: v for k, v in manifest.items() if k != "signature"})
        if not hmac.compare_digest(expected, actual or ""):
            print("FAIL: manifest signature does not match")
            return 1
    failures = 0
    for chunk in manifest.get("chunks", []):
        path = manifest_path.parent / chunk["file"]
        if not path.exists():
            print(f"FAIL: missing chunk {path}")
            failures += 1
            continue
        digest = sha256_file(path)
        if digest != chunk["sha256"]:
            print(f"FAIL: checksum mismatch for {path.name}")
            failures += 1
            continue
        rows = 0
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for _line in handle:
                rows += 1
        if rows != chunk["rows"]:
            print(f"FAIL: {path.name} has {rows} rows, manifest says {chunk['rows']}")
            failures += 1
            continue
        print(f"  OK  {path.name}: {rows} rows, sha256 {digest[:12]}...")
    if failures:
        print(f"FAIL: {failures} chunk(s) failed verification")
        return 1
    print(f"PASS: {len(manifest.get('chunks', []))} chunk(s) verified")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", help="archive rows older than this date (YYYY-MM-DD)")
    parser.add_argument("--chunk-days", type=int, default=30, help="chunk size in days")
    parser.add_argument("--output", default="/tmp/ledger-archive", help="archive directory")
    parser.add_argument("--keep-days", type=int, default=90, help="never archive newer than this")
    parser.add_argument("--apply", action="store_true", help="delete exported rows")
    parser.add_argument("--confirm-delete", action="store_true", help="confirm deletion")
    parser.add_argument("--verify", metavar="MANIFEST", help="verify an archive manifest")
    args = parser.parse_args()
    if args.verify:
        return verify(args)
    if not args.before:
        parser.error("--before is required unless --verify is used")
    return archive(args)


if __name__ == "__main__":
    sys.exit(main())
