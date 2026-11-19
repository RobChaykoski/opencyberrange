"""Seed a synthetic Fleet administrator for the training lab.

Run on the training host:

    FLEET_URL=http://127.0.0.1:8082 \
    FLEET_ADMIN_PASSWORD=... \
    python scripts/ecosystem_seed/seed_fleet.py

Everything here is fake training data. It is idempotent: if Fleet is already
set up, it leaves the existing admin alone.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("FLEET_URL", "http://127.0.0.1:8082").rstrip("/")
EMAIL = os.environ.get("FLEET_ADMIN_EMAIL", "admin@example.invalid")
NAME = os.environ.get("FLEET_ADMIN_NAME", "Training Admin")
# security-delta: allow credential-like assignment (synthetic lab password)
PASSWORD = os.environ.get("FLEET_ADMIN_PASSWORD", "TrainLab!2026#Student")

payload = {
    "admin": {"email": EMAIL, "name": NAME, "password": PASSWORD},
    "org_info": {"org_name": "Training Lab", "org_logo_url": ""},
    "server_url": BASE,
}

request = urllib.request.Request(
    f"{BASE}/api/v1/setup",
    data=json.dumps(payload).encode("utf-8"),
    method="POST",
    headers={"Content-Type": "application/json", "Accept": "application/json"},
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()
    print(f"Fleet setup complete for {EMAIL}.")
except urllib.error.HTTPError as error:
    body = error.read().decode("utf-8", "replace")
    if error.code == 404 or (
        error.code in (400, 409, 422) and "already" in body.lower()
    ):
        print("Fleet is already set up; leaving the existing admin alone.")
    else:
        print(f"Fleet setup failed: {error.code}: {body[:400]}", file=sys.stderr)
        sys.exit(1)
