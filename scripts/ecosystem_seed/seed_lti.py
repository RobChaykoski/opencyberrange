"""Register the training Moodle as an LTI 1.3 platform in OCR dev.

Run inside the dev backend container:

    docker exec -i -e MOODLE_ISSUER=... ocr-backend python - < scripts/ecosystem_seed/seed_lti.py

The script is idempotent. It updates the registered platform URLs and creates a
local tool RSA key on first use, so the same command also enables Deep Linking
responses and AGS client assertions.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.crypto import encrypt_secret
from app.database import SessionLocal
from app.models import LtiPlatform
from app.services import lti as lti_service

ISSUER = os.environ.get(
    "MOODLE_ISSUER", "https://moodle.172.16.16.44.sslip.io:9443"
).rstrip("/")
INTERNAL_URL = os.environ.get("MOODLE_INTERNAL_URL", ISSUER).rstrip("/")
CLIENT_ID = os.environ.get("MOODLE_LTI_CLIENT_ID", "ocr-training-client").strip()
DEPLOYMENT_ID = os.environ.get("MOODLE_LTI_DEPLOYMENT_ID", "1").strip()
PLATFORM_NAME = os.environ.get(
    "MOODLE_PLATFORM_NAME", "Training Moodle"
).strip() or "Training Moodle"

if not CLIENT_ID:
    raise SystemExit("MOODLE_LTI_CLIENT_ID is required")
if not DEPLOYMENT_ID:
    raise SystemExit("MOODLE_LTI_DEPLOYMENT_ID is required")


def _generate_private_key() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")


session = SessionLocal()
try:
    platform = (
        session.query(LtiPlatform)
        .filter(
            LtiPlatform.issuer == ISSUER,
            LtiPlatform.client_id == CLIENT_ID,
            LtiPlatform.deployment_id == DEPLOYMENT_ID,
        )
        .first()
    )
    if platform is None:
        platform = LtiPlatform(
            name=PLATFORM_NAME,
            issuer=ISSUER,
            client_id=CLIENT_ID,
            deployment_id=DEPLOYMENT_ID,
            auth_login_url=f"{ISSUER}/mod/lti/auth.php",
            token_url=f"{INTERNAL_URL}/mod/lti/token.php",
            jwks_url=f"{INTERNAL_URL}/mod/lti/certs.php",
            enabled=True,
        )
        session.add(platform)
        key_state = "generated"
    else:
        platform.auth_login_url = f"{ISSUER}/mod/lti/auth.php"
        platform.token_url = f"{INTERNAL_URL}/mod/lti/token.php"
        platform.jwks_url = f"{INTERNAL_URL}/mod/lti/certs.php"
        platform.enabled = True
        key_state = "existing"

    if not (platform.private_key or "").strip():
        platform.private_key = encrypt_secret(_generate_private_key())
        key_state = "generated"

    session.commit()
    session.refresh(platform)

    # Create or reuse the local identity provider now so the first launch does
    # not have to do it on the hot path.
    lti_service._get_provider(session, platform)

    print(
        f"Registered LTI platform id={platform.id} issuer={ISSUER} "
        f"internal={INTERNAL_URL} client_id={CLIENT_ID} "
        f"deployment_id={DEPLOYMENT_ID} private_key={key_state}"
    )
finally:
    session.close()
