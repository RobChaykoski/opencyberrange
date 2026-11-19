"""Register the training Moodle as an LTI 1.3 platform in OCR dev.

Run inside the dev backend container:

    docker exec -i -e MOODLE_ISSUER=... ocr-backend python - < scripts/ecosystem_seed/seed_lti.py
"""

from __future__ import annotations

import os

from app.database import SessionLocal
from app.models import LtiPlatform

ISSUER = os.environ.get(
    "MOODLE_ISSUER", "https://moodle.172.16.16.44.sslip.io:9443"
).rstrip("/")
CLIENT_ID = os.environ.get("MOODLE_LTI_CLIENT_ID", "ocr-training-client")
DEPLOYMENT_ID = os.environ.get("MOODLE_LTI_DEPLOYMENT_ID", "1")

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
            name="Training Moodle",
            issuer=ISSUER,
            client_id=CLIENT_ID,
            deployment_id=DEPLOYMENT_ID,
            auth_login_url=f"{ISSUER}/mod/lti/auth.php",
            token_url=f"{ISSUER}/mod/lti/token.php",
            jwks_url=f"{ISSUER}/mod/lti/certs.php",
            enabled=True,
        )
        session.add(platform)
    else:
        platform.name = "Training Moodle"
        platform.auth_login_url = f"{ISSUER}/mod/lti/auth.php"
        platform.token_url = f"{ISSUER}/mod/lti/token.php"
        platform.jwks_url = f"{ISSUER}/mod/lti/certs.php"
        platform.enabled = True
    session.commit()
    print(
        f"Registered LTI platform id={platform.id} issuer={ISSUER} "
        f"client_id={CLIENT_ID} deployment_id={DEPLOYMENT_ID}"
    )
finally:
    session.close()
