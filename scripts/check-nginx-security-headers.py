"""Static regression check for the SPA security headers.

nginx drops inherited add_header directives when a location declares its own.
This check ensures the shared snippet is included in the SPA entry point and
the deep-link fallback, that the LTI embed locations use their relaxed policy,
and that both snippets still carry the expected controls.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "platform" / "frontend"

SNIPPET = FRONTEND / "security-headers.conf"
NGINX_FILES = [FRONTEND / "nginx.conf", FRONTEND / "nginx-ssl.conf"]

REQUIRED_SNIPPET_MARKERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Strict-Transport-Security",
]
INCLUDE = "include /etc/nginx/snippets/security-headers.conf;"
EMBED_SNIPPET = FRONTEND / "lti-embed-headers.conf"
EMBED_INCLUDE = "include /etc/nginx/snippets/lti-embed-headers.conf;"
EMBED_MARKERS = [
    "Content-Security-Policy",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
]
EMBED_LOCATIONS = ("location = /lti/deep-link", "location = /lti/callback")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    failures.append(message)


failures: list[str] = []

if not SNIPPET.exists():
    fail("platform/frontend/security-headers.conf is missing")
else:
    snippet = SNIPPET.read_text(encoding="utf-8")
    for marker in REQUIRED_SNIPPET_MARKERS:
        if marker not in snippet:
            fail(f"security-headers.conf is missing {marker}")
    if "frame-src 'self' https://*:8443" not in snippet:
        fail("security-headers.conf must allow the dedicated workbook origin frame")

for path in NGINX_FILES:
    if not path.exists():
        fail(f"{path.name} is missing")
        continue
    text = path.read_text(encoding="utf-8")
    count = text.count(INCLUDE)
    if count < 2:
        fail(f"{path.name} includes the security snippet {count} time(s), expected at least 2")
    for location in ("location = /index.html", "location / {"):
        if location not in text:
            fail(f"{path.name} is missing {location}")
    if EMBED_INCLUDE not in text:
        fail(f"{path.name} does not include the LTI embed snippet")
    for location in EMBED_LOCATIONS:
        if location not in text:
            fail(f"{path.name} is missing {location}")

if not EMBED_SNIPPET.exists():
    fail("platform/frontend/lti-embed-headers.conf is missing")
else:
    embed = EMBED_SNIPPET.read_text(encoding="utf-8")
    for marker in EMBED_MARKERS:
        if marker not in embed:
            fail(f"lti-embed-headers.conf is missing {marker}")
    if "frame-ancestors https:" not in embed:
        fail("lti-embed-headers.conf must allow an HTTPS LMS frame")
    if "form-action 'self' https:" not in embed:
        fail("lti-embed-headers.conf must allow the HTTPS LMS return POST")
    if "http://localhost:*" not in embed:
        fail("lti-embed-headers.conf must allow a local HTTP LMS for development")
    if "add_header X-Frame-Options" in embed:
        fail("lti-embed-headers.conf must not send X-Frame-Options")

if failures:
    sys.exit(1)

print("PASS: nginx SPA and LTI embed security headers are wired")
