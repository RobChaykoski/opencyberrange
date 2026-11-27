# LTI

## Purpose

Let a Moodle or other LMS course launch an OpenCyberRange exercise without a
second password, and optionally deep-link an exercise into the course.

## Flow

1. The LMS sends an OIDC login initiation to `/api/lti/login`.
2. The platform returns an authentication request.
3. The LMS posts the launch to `/api/lti/launch`.
4. The platform validates the JWT signature, issuer, audience, deployment,
   nonce, and message type.
5. The platform maps the LMS subject to a local user and starts a session.
6. Deep linking uses the platform's assignment selection and returns the chosen
   exercise to the LMS.
7. Grade passback, where configured, uses the LTI assignment and score service.

## Configuration

| Item | Where |
|---|---|
| Platform registration | Admin -> LTI platforms |
| Client ID, issuer, deployment ID | from the LMS |
| Public keys | platform JWKS endpoint |
| Launch URL | `/api/lti/launch` |
| Deep-link URL | `/api/lti/deep-link` |

## Rules

- Treat the LMS as a launch context, not the source of truth for grades.
- Validate every JWT claim; do not trust the LMS display name.
- Do not create an administrator from an LTI role.
- A platform-scoped course must still pass the normal course checks.
- Log launch failures as security events without logging the raw JWT.

## Tests

```bash
cd platform/backend
python -m pytest tests/test_lti.py tests/test_sso_gate.py -q
```

## Related

- [LTI documentation](../../../docs/LTI.md)
- [Moodle LTI showcase](../../../docs/MOODLE-LTI-SHOWCASE.md)
- [Backend SSO and LTI](../../backend/features/sso-and-lti/README.md)
