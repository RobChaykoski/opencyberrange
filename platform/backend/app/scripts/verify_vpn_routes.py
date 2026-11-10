#!/usr/bin/env python3
"""Verify that the WireGuard route covers every lab for each student.

Checks:
  * each stored client address is outside the old 10.0.0.0/16 pool;
  * the generated client config uses a /32 interface address;
  * the client AllowedIPs is exactly the student's own lab /24;
  * every active lab maps to that same /24 (the session subnet is per user);
  * the Peer Manager peer exists with allowed_ips = client_ip/32.

Usage (inside the backend container):
  python /app/app/scripts/verify_vpn_routes.py
  python /app/app/scripts/verify_vpn_routes.py --all
"""
import argparse
import ipaddress
import sys

sys.path.insert(0, "/app")

from app.config import settings
from app.database import SessionLocal
from app.models import Lab, WireGuardConfig
from app.routers.labs import get_subnet_id, vpn_allowed_ips, vpn_lab_subnet
from app.services.wireguard_manager import WireGuardManager

OLD_CLIENT_POOL = ipaddress.ip_network("10.0.0.0/16")
LAB_POOLS = [
    ipaddress.ip_network("10.100.0.0/14"),
    ipaddress.ip_network("10.104.0.0/13"),
    ipaddress.ip_network("10.112.0.0/12"),
    ipaddress.ip_network("10.128.0.0/9"),
    ipaddress.ip_network("10.50.0.0/16"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Check every stored client, not just a sample.")
    args = parser.parse_args()

    db = SessionLocal()
    manager = WireGuardManager(api_url=settings.WG_API_URL, api_key=settings.WG_API_KEY)
    failures = []

    try:
        configs = db.query(WireGuardConfig).order_by(WireGuardConfig.user_id).all()
        if not configs:
            print("No WireGuard clients found; nothing to verify.")
            return 0
        if not args.all:
            configs = configs[:1]

        labs = db.query(Lab).filter(Lab.is_active == True).all()
        peers = manager.list_peers()
        peer_map = {}
        if peers is not None:
            peer_map = {p.get("public_key", "").strip(): p for p in peers}

        print(f"client base: {settings.WG_CLIENT_BASE}")
        print(f"active labs: {len(labs)}; clients checked: {len(configs)}")

        for config in configs:
            client_ip = ipaddress.ip_address(config.client_ip)
            allowed = vpn_allowed_ips(config.user_id)
            allowed_net = ipaddress.ip_network(allowed)
            expected = f"10.{get_subnet_id(config.user_id)[0]}.{get_subnet_id(config.user_id)[1]}.0/24"

            if client_ip in OLD_CLIENT_POOL:
                failures.append(f"user {config.user_id}: client {client_ip} is in the old 10.0.0.0/16 pool")
            if allowed != expected:
                failures.append(f"user {config.user_id}: route {allowed} != expected {expected}")
            if not any(allowed_net.subnet_of(pool) for pool in LAB_POOLS):
                failures.append(f"user {config.user_id}: route {allowed} is outside the lab firewall pools")

            config_text = manager.generate_client_config(
                private_key="PRIVATE_KEY_PLACEHOLDER",
                client_ip=config.client_ip,
                server_public_key="SERVER_PUBLIC_KEY_PLACEHOLDER",
                server_endpoint="vpn.example:51820",
                allowed_ips=allowed,
            )
            if f"Address = {config.client_ip}/32" not in config_text:
                failures.append(f"user {config.user_id}: generated config does not use a /32 address")
            if f"AllowedIPs = {allowed}" not in config_text:
                failures.append(f"user {config.user_id}: generated config does not route {allowed}")

            # The session subnet is per user, but check every active lab explicitly
            # so a future per-lab allocator cannot silently break the VPN route.
            for lab in labs:
                second, third = get_subnet_id(config.user_id, lab.slug)
                lab_subnet = f"10.{second}.{third}.0/24"
                if lab_subnet != allowed:
                    failures.append(
                        f"user {config.user_id}: lab {lab.slug} maps to {lab_subnet}, route is {allowed}"
                    )
                    break

            peer = peer_map.get(config.public_key.strip())
            if peers is not None and not peer:
                failures.append(f"user {config.user_id}: no Peer Manager peer for the public key")
            elif peer:
                peer_allowed = (peer.get("allowed_ips") or "").strip()
                if peer_allowed != f"{config.client_ip}/32":
                    failures.append(
                        f"user {config.user_id}: peer allowed_ips {peer_allowed!r} != {config.client_ip}/32"
                    )

            print(
                f"  user {config.user_id}: {config.client_ip}/32 -> {allowed}; "
                f"{len(labs)} labs checked"
            )

        if failures:
            print("\nVPN route verification FAILED:")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("\nVPN route verification passed: every checked lab is covered by the student's /24.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
