# Identity Providers (SSO)

Use **Admin → Settings → Identity providers** to let learners and staff sign in
with an institution account. The platform supports OIDC, SAML 2.0, and LDAP /
Active Directory. The local username and password form stays available.

## Before you start

- Have the public origin ready, for example `https://range.example.edu`. The
  redirect and ACS URLs are built from it.
- Decide whether new accounts are auto-provisioned, auto-approved, and whether a
  verified email may link an existing student or instructor account.
- Keep at least one local administrator account as break-glass access. External
  identities never receive the administrator role.

## Add an OIDC provider

1. Create an application at the IdP (or use CAF, if your institution is a
   member). Register the redirect URI shown on the provider card:

   ```text
   https://<public-origin>/api/auth/sso/oidc/<provider-id>/callback
   ```

2. In **Identity providers**, choose **OpenID Connect** and enter the issuer,
   client ID, client secret, and scopes (`openid email profile` by default).
3. Map the username, email, name, and groups claims if your IdP uses different
   names.
4. Select **Test** to check discovery and signing keys.
5. Enable the provider and sign out. The login page now shows
   **Sign in with …**.

For RP-initiated logout, register `https://<public-origin>/login` as the
post-logout redirect. Without it, logout stays local.

## Add a SAML 2.0 provider

1. Create a SAML application and register the SP entity ID and ACS URL shown on
   the provider card:

   ```text
   https://<public-origin>/api/auth/sso/saml/<provider-id>/acs
   ```

2. Enter the IdP entity ID, SSO URL, signing certificate, and attribute
   mapping. Assertions must be signed.
3. Select **Test**, then enable the provider.

## Add an LDAP / Active Directory provider

1. Enter an `ldaps://` URL (or an `ldap://` URL with StartTLS), the base DN, and
   a read-only service bind account.
2. Set the user search filter, for example `(sAMAccountName={username})` for
   Active Directory or `(uid={username})` for OpenLDAP.
3. Map email, username, name, and group attributes. For OpenLDAP, the group
   attribute is usually `memberOf`; ensure the directory's memberOf overlay is
   enabled.
4. Set the instructor group if group membership should grant the instructor
   role. Use the group DN, for example
   `cn=instructors,ou=groups,dc=example,dc=org`.
5. Select **Test** to verify the service bind and search.

The login page shows a directory form for each enabled LDAP provider.

## Account policy

- The provider + subject pair is the stable identity; email is not the key.
- A new external identity can create a student or instructor account. It can
  never create an administrator.
- An existing local account is linked only by a verified email, and never if it
  is an administrator account.
- SSO-provisioned accounts cannot use the local password form.
- Directory role mapping is applied at provisioning and **refreshed on every SSO
  login**, so a group change takes effect without editing the account.

## Secrets and privacy

- Bind passwords, client secrets, SAML private keys, and OIDC ID tokens are
  encrypted with the platform key. The API never returns a secret; it reports
  only which secret keys are present.
- Identity data appears in the learner's subject-access export and is removed on
  erasure. See [Privacy, Erasure, and Backups](27_Privacy_And_Erasure.md).
- Provider test actions make outbound requests to the configured URLs. Configure
  only trusted IdP endpoints.

## Test with the local stack

For a lab or pilot, the repository includes a profile-gated Dex + OpenLDAP test
stack. See [the SSO test stack README](https://github.com/RobChaykoski/opencyberrange/blob/main/deploy/sso/README.md). It is not a
production identity provider.

## Troubleshooting

| Symptom | Check |
|---|---|
| `sso_error=unavailable` after clicking the provider | The backend cannot reach the issuer. Check `PUBLIC_BASE_URL`, DNS, TLS, and `SSO_ALLOW_INSECURE_HTTP` (test hosts only). |
| Redirect URI mismatch at the IdP | The provider card's callback URL must match exactly, including scheme, host, port, and provider ID. |
| OIDC discovery works but the callback fails | Check the ID token issuer, audience, nonce, and signing keys. The backend log records a safe reason. |
| LDAP bind succeeds but users fail | Check the user search filter, base DN, and whether the user can rebind. |
| Everyone signs in as a student | Check the group attribute and instructor group DN. |
| Login works but the role does not change | The role refreshes on the next SSO login; sign out and back in. |

Do not paste provider secrets or ID tokens into a support ticket.

## Related

- [OIDC guide](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/SSO-OIDC.md)
- [SAML and LDAP guide](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/SSO-SAML-LDAP.md)
- [SSO HA contract](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/decisions/0004-sso-ha-contract.md)
- [Compliance posture](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/COMPLIANCE.md)
