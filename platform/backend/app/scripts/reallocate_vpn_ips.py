#!/usr/bin/env python3
"""Reallocate WireGuard client IPs to the configured client base.

The default is a dry run. Use --apply to update the database and re-register
each peer with the Peer Manager. Private keys are not changed; students must
re-download their VPN configuration after the migration.

Usage (inside the backend container):
  python /app/app/scripts/reallocate_vpn_ips.py
  python /app/app/scripts/reallocate_vpn_ips.py --apply
"""
import argparse
import sys

sys.path.insert(0, "/app")

from app.config import settings
from app.database import SessionLocal
from app.models import WireGuardConfig
from app.routers.labs import get_vpn_client_ip
from app.services.wireguard_manager import WireGuardManager


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Update the database and Peer Manager. Without this flag the script only prints the plan.",
    )
    parser.add_argument(
        "--base",
        default="",
        help="Client base override, for example 10.255. Defaults to settings.WG_CLIENT_BASE.",
    )
    args = parser.parse_args()

    base = args.base or settings.WG_CLIENT_BASE
    manager = WireGuardManager(
        api_url=settings.WG_API_URL,
        api_key=settings.WG_API_KEY,
    )
    db = SessionLocal()

    try:
        configs = db.query(WireGuardConfig).order_by(WireGuardConfig.user_id).all()
        if not configs:
            print("No WireGuard clients found; nothing to do.")
            return 0

        used = set()
        plan = []
        for config in configs:
            offset = 0
            while True:
                candidate = get_vpn_client_ip(config.user_id + offset, base)
                if candidate not in used:
                    used.add(candidate)
                    break
                offset += 1
            plan.append((config, candidate))

        changed = [(config, new_ip) for config, new_ip in plan if config.client_ip != new_ip]
        print(f"client base: {base}")
        print(f"clients: {len(plan)}; changing: {len(changed)}")
        for config, new_ip in changed:
            print(f"  user {config.user_id}: {config.client_ip} -> {new_ip}")

        if not changed:
            print("All clients already use the configured base.")
            return 0

        if not args.apply:
            print("Dry run only. Re-run with --apply to update the rows and peers.")
            return 0

        failures = 0
        for config, new_ip in changed:
            old_ip = config.client_ip
            # sync_peer only adds a missing peer, so remove first to replace the
            # old allowed_ips with the new /32.
            manager.remove_peer(config.public_key)
            if manager.add_peer(config.public_key, new_ip):
                config.client_ip = new_ip
                db.commit()
                print(f"  [ok] user {config.user_id}: {old_ip} -> {new_ip}")
            else:
                # Keep the old address working rather than leaving the student
                # with a database row that no peer serves.
                config.client_ip = old_ip
                db.commit()
                manager.add_peer(config.public_key, old_ip)
                failures += 1
                print(f"  [warn] user {config.user_id}: peer update failed; kept {old_ip}")
        print("Migration complete. Students must download a fresh VPN configuration.")
        print(f"Peer re-add failures: {failures}")
        return 1 if failures else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
