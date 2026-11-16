# Integrations

Connecting the platform to an institution's identity, learning, and content
systems.

| Document | Use it for |
|---|---|
| [LTI 1.3](../LTI.md) | Moodle/Canvas launch, AGS, NRPS, and Deep Linking |
| [SSO with OIDC](../SSO-OIDC.md) | OpenID Connect providers |
| [SSO with SAML and LDAP](../SSO-SAML-LDAP.md) | SAML 2.0 and directory providers |
| [Identity providers](../../Manual-Lite/04_Admin_Guide/30_Identity_Providers.md) | The admin configuration walkthrough |
| [Wiki origin split](../WIKI-ORIGIN-SPLIT.md) | The separate 8443 workbook origin |
| [Exercise export and import](../EXERCISE-EXPORT-IMPORT.md) | Moving lab content between installs |
| [Manual publishing](../MANUAL-PUBLISHING.md) | Building and publishing the manual |
| [External datasets](../SECURITY-DATASETS.md) | Reviewed data sources and attribution |
| [Reverse proxy](../REVERSE-PROXY.md) | TLS and origin layout |

## Rules

- An identity provider is configured by an administrator; a client cannot
  choose its tenant or role claim.
- LTI links verify the issuer, client, deployment, nonce, and state before a
  launch is accepted.
- An external dataset needs a reviewed inventory entry, attribution, a pin, and
  a content hash.
- Do not add a live public target without the lab-safety and external-target
  review.
