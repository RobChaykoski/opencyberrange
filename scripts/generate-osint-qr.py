"""Generate a QR code for a public OSINT exercise URL.

Usage:
    python scripts/generate-osint-qr.py \
      --url "https://www.linkedin.com/in/example/" \
      --out platform/labs/OSINT/osint-3-2-public-profile/assets/profile-qr.png

Only put a public URL in the QR code. Do not encode a token, password, learner
record, or private link.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

import qrcode


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an OSINT exercise QR code")
    parser.add_argument("--url", required=True, help="Public URL to encode")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--box-size", type=int, default=8, help="QR module size in pixels")
    parser.add_argument("--border", type=int, default=4, help="Quiet-zone modules")
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print("Refusing to encode a non-HTTP(S) URL.")
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
