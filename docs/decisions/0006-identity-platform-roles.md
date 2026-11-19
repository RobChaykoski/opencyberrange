# ADR 0006: Identity platform roles

- Status: accepted
- Date: 2026-11-19

## Context

OpenCyberRange, OpenGRC, OpenDLP, Moodle, and the wiki all need single sign-on,
MFA, and group-based application access. The identity curriculum also needs to
teach enterprise federation and identity governance. One platform cannot be both
the lowest-friction production SSO service and the most complete advanced-IAM
teaching environment without making daily operations harder than they need to be.

## Decision

Use three identity platforms with distinct roles:

| Platform | Role | Use |
|---|---|---|
| Authentik | Operational identity provider | OpenCyberRange, OpenGRC, OpenDLP, Moodle, and wiki SSO; LDAP integration; OIDC; MFA; self-service password reset |
| Keycloak | Advanced enterprise-IAM lab | Realms, clients, mappers, brokering, OIDC and SAML internals, multi-tenant and architecture exercises |
| OpenIAM | Identity governance lab | Joiner/mover/leaver, provisioning, access certification, RBAC, segregation of duties, role mining |

Authentik is the default for production-style authentication because its user,
group, application, policy, SSO, and MFA model is easier to teach and operate.
Keycloak is not the operational default. OpenIAM is not an authentication
front-end in this architecture; it is the governance layer.

## Target architecture

```text
                    OpenIAM
             (identity governance)

                         |
                         v

                   Authentik
              (primary identity)

                /      |      \
               /       |       \
      OpenCyberRange  OpenGRC  OpenDLP

                         |
                         v

                     Keycloak
           (advanced federation lab)
```

The arrows describe learning and governance relationships. They do not require a
single production request path through all three platforms.

## Curriculum consequences

The identity pathway becomes four learning tracks:

1. **Identity Fundamentals** — Authentik: users, groups, MFA, policies, and
   application access.
2. **Enterprise SSO** — Authentik: OAuth2, OIDC, SAML, LDAP, and federation.
3. **Enterprise IAM** — Keycloak: realms, clients, mappers, brokering, and
   identity architecture.
4. **Identity Governance** — OpenIAM: lifecycle, access reviews, certification,
   role mining, and segregation of duties.

Career targets:

| Track | Target roles |
|---|---|
| Identity Fundamentals | Junior Security Analyst, Helpdesk, System Administrator |
| Enterprise SSO | IAM Analyst, Identity Engineer |
| Enterprise IAM | IAM Engineer, Security Architect |
| Identity Governance | IGA Analyst, Compliance Analyst, Identity Governance Specialist |

## Consequences

- Production SSO work should target Authentik first.
- Keycloak labs are explicitly advanced and must not be framed as the platform
  that runs the ecosystem.
- OpenIAM labs follow the official documentation and focus on governance, not
  authentication.
- The existing generic OIDC/SAML identity-provider support remains; Authentik is
  the recommended provider preset, not a hard dependency.
- A future deployment guide must cover Authentik, LDAP, OIDC, MFA, and
  self-service password reset as one operational runbook.

## Non-goals

- Running all three platforms for every learner.
- Making Keycloak the default SSO provider.
- Using OpenIAM as a replacement for Authentik authentication.
- Teaching all three platforms with equal depth in the fundamentals track.
