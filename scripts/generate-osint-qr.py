"""Generate a QR code for an offline OSINT exercise URL.

Usage:
    python scripts/generate-osint-qr.py \
      --url "http://connect.lab:8080/" \
      --out platform/labs/OSINT/osint-2-4-public-profile/assets/profile-qr.png

The generator is deliberately restricted to lab-local and documentation hosts.
It refuses social-media profiles and other public third-party targets so a
fictional exercise cannot accidentally encode a real person's profile.
"""

from __future__ import annotations

import argparse
import ipaddress
from pathlib import Path
from urllib.parse import urlparse

import qrcode

ALLOWED_SUFFIXES = (".lab", ".example", ".invalid", ".test", ".local")
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _allowed_host(hostname: str) -> bool:
    host = (hostname or "").strip().lower().rstrip(".")
    if not host:
        return False
    if host in ALLOWED_HOSTS:
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return host.endswith(ALLOWED_SUFFIXES)
    return address.is_private or address.is_loopback or address.is_link_local


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an offline OSINT exercise QR code")
    parser.add_argument("--url", required=True, help="Lab-local or documentation URL to encode")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--box-size", type=int, default=8, help="QR module size in pixels")
    parser.add_argument("--border", type=int, default=4, help="Quiet-zone modules")
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print("Refusing to encode a non-HTTP(S) URL.")
        return 2
    if not _allowed_host(parsed.hostname or ""):
        print(
            "Refusing to encode a public third-party target. "
            "Use a .lab, .example, .invalid, .test, or private address."
        )
        return 2

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=max(2, args.box_size),
        border=max(0, args.border),
    )
    qr.add_data(args.url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
