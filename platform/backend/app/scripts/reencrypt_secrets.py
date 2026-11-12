"""Move stored secrets onto the current Fernet key.

Run this after rotating ``WG_ENCRYPTION_KEY`` and setting
``WG_ENCRYPTION_KEY_PREVIOUS`` to the old key(s). The app can already read old
rows through MultiFernet; this pass rewrites them with the new key so the old
key can be dropped.

Usage:
    python -m app.scripts.reencrypt_secrets --dry-run
    python -m app.scripts.reencrypt_secrets --apply
"""

from __future__ import annotations

import argparse

from app.crypto import decrypt_secret, encrypt_secret, is_encrypted, needs_reencryption
from app.database import SessionLocal
from app.models import InstructorApiKey, User, WireGuardConfig


def _rewrite(label: str, value: str, *, apply: bool) -> tuple[bool, str | None]:
    """Return (changed, new_value_or_error)."""
    if not value:
        return False, None
    if not is_encrypted(value):
        # Legacy plaintext row: encrypt it directly instead of trying to
        # decrypt a value that was never a Fernet token.
        return True, encrypt_secret(value) if apply else None
    if not needs_reencryption(value):
        return False, None
    try:
        plaintext = decrypt_secret(value)
    except Exception as exc:  # malformed rows should not stop the pass
        return False, f"{label}: {exc}"
    if not apply:
        return True, None
    return True, encrypt_secret(plaintext)


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-encrypt stored secrets")
    parser.add_argument("--apply", action="store_true", help="Write the changes")
    parser.add_argument("--dry-run", action="store_true", help="Only report changes")
    args = parser.parse_args()
    apply = bool(args.apply and not args.dry_run)

    db = SessionLocal()
    changed = 0
    failed = 0
    checked = 0
    try:
        for user in db.query(User).filter(User.totp_secret.isnot(None)).all():
            checked += 1
            label = f"user:{user.username}:totp_secret"
            did_change, result = _rewrite(label, user.totp_secret, apply=apply)
            if result and result.startswith(f"{label}:"):
                print(result)
                failed += 1
            elif did_change:
                if result:
                    user.totp_secret = result
                changed += 1

        for row in db.query(WireGuardConfig).all():
            checked += 1
            label = f"wireguard:{row.id}:private_key"
            did_change, result = _rewrite(label, row.private_key, apply=apply)
            if result and result.startswith(f"{label}:"):
                print(result)
                failed += 1
            elif did_change:
                if result:
                    row.private_key = result
                changed += 1

        for row in db.query(InstructorApiKey).filter(
            InstructorApiKey.encrypted_key.isnot(None)
        ).all():
            checked += 1
            label = f"instructor_api_key:{row.id}:encrypted_key"
            did_change, result = _rewrite(label, row.encrypted_key, apply=apply)
            if result and result.startswith(f"{label}:"):
                print(result)
                failed += 1
            elif did_change:
                if result:
                    row.encrypted_key = result
                changed += 1

        if apply and changed:
            db.commit()
        elif apply:
            db.rollback()
        print(
            f"{'Applied' if apply else 'Would change'} {changed} of {checked} "
            f"stored secret(s); {failed} row(s) need manual review."
        )
        return 1 if failed else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
