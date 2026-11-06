# SAML and LDAP single sign-on

Status: **Enterprise 3.1.1**.

This guide covers the SAML 2.0 and LDAP / Active Directory adapters. For OIDC,
see [`SSO-OIDC.md`](SSO-OIDC.md). All three adapters share the HA contract in
[ADR 0004](decisions/0004-sso-ha-contract.md), the provisioning policy, and the
one-time SPA exchange ticket.

Keep a local break-glass administrator account. SSO never creates or links an
administrator automatically.

## Shared behaviour

- The login flow can start on one API replica and finish on another. Flow state
  and one-time tickets live in PostgreSQL.
- New accounts can be provisioned automatically. They are always `student` or
  `instructor`, never `admin`.
- SSO-provisioned accounts have `password_login_disabled=true`. Local password
  login is not available for them.
- Existing accounts are linked by verified email only. Administrator accounts
  are never auto-linked.
- `auto_approve=false` creates the account in a pending state and issues no
  ticket until an administrator approves it.
- The provider test button validates SAML settings or performs an LDAP service
  bind, depending on the provider type.

## SAML 2.0

### Platform configuration

Add a provider with type **SAML 2.0**:

| Field | Required | Notes |
|---|---|---|
| IdP entity ID | Yes | The issuer/entity ID in the IdP metadata |
| SP entity ID | Yes | Register this exact value at the IdP |
| SSO URL | Yes | The IdP HTTP-Redirect single sign-on endpoint |
| ACS URL | No | Leave blank to derive `https://<public-origin>/api/auth/sso/saml/<id>/acs` |
| IdP X.509 certificate | Yes | Public signing certificate; PEM or base64 |
| SLO URL | No | Stored for future SLO use |
| SP X.509 certificate | No | Needed only for signed AuthnRequests |
| SP private key | No | Secret; needed with the SP certificate for signed AuthnRequests |
| Email attribute | Yes | Defaults to `email` |
| Username attribute | No | Defaults to `uid` |
| First/last/display name | No | Defaults to `givenName`, `sn`, `displayName` |
| Group attribute | No | Defaults to `groups` |
| Instructor group | No | Group value that grants the instructor role |

The provider card shows the exact ACS URL after saving. Register that URL and
the SP entity ID at the IdP. The IdP must send an **email** attribute or claim.

### Identity provider setup

1. Create a SAML application at the IdP.
2. Set the SP entity ID to the value configured in OpenCyberRange.
3. Set the ACS URL to the value shown in the provider card.
4. Download the IdP signing certificate and paste it into the provider config.
5. Add an email claim. Optionally add username, name, and group claims.
6. Assign users or groups to the application.
7. Save the provider, then use **Test** to validate the settings.

Common attribute names:

| IdP | Email | Groups |
|---|---|---|
| Okta | `email` | `groups` |
| Entra ID | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` | `http://schemas.microsoft.com/ws/2008/06/identity/claims/groups` |
| Google Workspace | `email` | `groups` |
| Keycloak | `email` | `groups` |

Set the attribute mapping fields to the exact names your IdP sends.

### Flow

1. The learner selects the SAML provider.
2. The backend creates a RelayState and stores it in `sso_login_states`.
3. The backend builds the AuthnRequest with `python3-saml` and stores its ID as
   the state nonce.
4. The IdP posts a signed assertion to the ACS.
5. The backend consumes the RelayState, validates the assertion, signature,
   audience, recipient, and InResponseTo, then links or provisions the account.
6. The SPA exchanges the one-time ticket for the platform JWT.

Only SP-initiated login is accepted. An unsolicited assertion without a
RelayState is rejected.

### Signed AuthnRequests

Provide both the SP certificate and the SP private key. The private key is
stored encrypted and is never returned by the API. If only one of the two is
present, AuthnRequests are unsigned.

### Logout

SAML logout is local in 3.1.1: the platform JWT is revoked, but the IdP session
is not ended. OIDC RP-initiated logout remains the only IdP logout path.

## LDAP and Active Directory

### Platform configuration

Add a provider with type **LDAP / Active Directory**:

| Field | Required | Notes |
|---|---|---|
| Server URL | Yes | `ldaps://...` or `ldap://...` with StartTLS |
| Start TLS | No | Required for `ldap://` unless development HTTP is allowed |
| Verify TLS | Yes | Keep enabled in production |
| Base DN | Yes | Search root for users |
| Bind DN | No | Service account used for search; anonymous search if blank |
| Bind password | No | Secret; stored encrypted |
| User search filter | Yes | Defaults to `(uid={username})` |
| Email attribute | Yes | Defaults to `mail` |
| Username attribute | No | Defaults to `uid` |
| Group attribute | No | Defaults to `memberOf` |
| Instructor group | No | Group name or DN that grants the instructor role |

Examples:

```text
# OpenLDAP
(uid={username})

# Active Directory
(sAMAccountName={username})
```

The service account needs permission to search the base DN. After the search,
the platform rebinds as the user's DN to verify the password, so LDAP does not
store user passwords.

### Flow

1. The learner enters a directory username and password on the login page.
2. The backend binds with the service account and searches for exactly one user.
3. The backend rebinds as that user to verify the password.
4. The backend maps attributes, links or provisions the account, and returns a
   one-time ticket.
5. The SPA exchanges the ticket for the platform JWT.

The user DN is the stable subject. Changing an email address does not break the
link; replacing the directory object does.

### TLS

Production deployments must use `ldaps://` or StartTLS. Certificate
verification is on by default. Disabling it is intended only for a controlled
lab directory.

## Roles and groups

`instructor_group` is compared against the groups returned by the provider:

- OIDC: the configured `groups_claim` (default `groups`), as an array or a
  comma/semicolon-separated string.
- SAML: the configured `group_attribute` values.
- LDAP: the configured `group_attribute` values, usually `memberOf` DNs.

A short value such as `instructors` matches both `instructors` and
`CN=Instructors,OU=Groups,DC=example,DC=edu`. Role mapping applies only when a
new account is provisioned. Existing accounts keep their current role.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| SAML ACS redirects with `sso_failed` | Signature, audience, recipient, or InResponseTo validation failed | Check the IdP certificate, SP entity ID, ACS URL, and server clock |
| SAML login start returns `sso_error=unavailable` | Invalid SAML settings, missing certificate, or unreachable configuration | Use the provider **Test** action and read the API log |
| SAML assertion has no email | The IdP is not sending the configured email attribute | Add the claim or correct `email_attribute` |
| LDAP form reports invalid credentials | Wrong password, wrong search filter, duplicate users, or no search permission | Test the service bind, verify the filter, and check the service account |
| LDAP form reports the directory is unavailable | Connection, TLS, or bind failure | Check `ldaps://`/StartTLS, the certificate, the bind DN, and the password |
| Account is pending approval | `auto_approve` is off | Approve the user in the admin UI |
| Existing user is not linked | Email is unverified, linking is disabled, or the account is an administrator | Link explicitly or use the local account |

## Local test notes

For a local harness, set `PUBLIC_BASE_URL` to the external origin and keep
`SSO_ALLOW_INSECURE_HTTP=false` unless you are deliberately testing a local IdP
or directory. `SSO_ALLOW_INSECURE_HTTP=true` permits `http://` OIDC issuers,
`http://` SAML SSO URLs, plain LDAP without StartTLS, and single-label hosts such
as `https://localhost`. Never enable it in production.
