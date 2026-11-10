# Chapter Review: The Community Centre Identity Incident

This review combines the three labs. There is no new target and no new flag.
The goal is to show that you can read identity evidence, name the failed
control, and choose a fix that addresses the cause rather than the symptom.

## Scenario

A community centre asked for an identity review after a volunteer reported
strange behaviour in the staff portal. The review found three separate problems:

1. A staff session cookie was Base64 of `user:role`, so a staff member could
   edit the cookie and become an administrator.
2. The portal's Community ID client accepted any redirect URI and did not use
   `state` or PKCE, so an authorization code could be delivered to another
   callback.
3. A volunteer coordinator left 14 months ago, but the account was still active
   and its `reports:admin` token still worked.

No customer data was changed. The centre wants a short, honest report and a
fix plan.

## Part A: Name the failed control

Match each finding to the identity control that failed. Use one answer per
finding.

| Finding | Candidate controls |
|---|---|
| 1. Forgeable session | Access review, session management, federation trust |
| 2. Open redirect | Session management, federation trust, password hashing |
| 3. Stale token | Access review, federation trust, cookie attributes |

## Part B: Evidence to preserve

For each finding, list the evidence you would collect before changing anything.
Consider:

- the raw `Cookie` or `Set-Cookie` header;
- the full `/authorize` URL, including `redirect_uri` and `state`;
- the authorization code, token response, and `/me` response;
- the directory row with status, last login, role, token, and scope;
- authentication and API logs for the affected account;
- the date and owner of the last access review.

## Part C: Fix order

You cannot fix everything at once. Put these actions in a sensible order and
explain the first one:

1. Disable the leaver account and revoke its tokens.
2. Replace client-side session state with a server-side session store.
3. Register an exact redirect URI allowlist and require `state` and PKCE.
4. Add MFA re-checks for sensitive administrator actions.
5. Schedule a quarterly access review with a named reviewer.

Consider which action reduces the most immediate risk, and which actions depend
on each other.

## Part D: Five-line incident summary

Write a short summary for a non-technical manager. Use this shape:

```text
What happened:
Who was affected:
What we found:
What we changed first:
What we will do next:
```

Keep it factual. Do not include real names, tokens, or passwords. Do not blame
the volunteer who reported the issue.

## Answer Key

### Part A

1. **Session management.** The server trusted a client-controlled role instead
   of a server-side session record.
2. **Federation trust.** The provider accepted an unregistered callback, and the
   client did not bind the request with `state` or PKCE.
3. **Access review.** The leaver account and its token were never removed.

### Part B

Accept any answer that names concrete artefacts: the raw cookie header, the
authorize URL and callback, the code and token exchange, the directory row and
scope, the account's authentication/API logs, and the last review record.

### Part C

A strong order starts with **disable the leaver and revoke the token**, because
that closes an active path with no legitimate owner. Then replace the session
design, then fix the federation controls, then add re-authentication and a
review schedule. Some teams fix the session and federation issues first if the
leaver token has already been revoked; the important part is to explain why.

### Part D

A strong summary is short, factual, and names the three causes without exposing
credentials. It should say what changed first and what remains.

## Self-Assessment

- [ ] I can explain the difference between authentication and authorization.
- [ ] I can explain why a Base64 `user:role` cookie is not a session.
- [ ] I can name the cookie attributes that limit session theft.
- [ ] I can explain redirect URI allowlisting, `state`, and PKCE.
- [ ] I can explain why a disabled account is not enough if its token works.
- [ ] I can describe a joiner, mover, and leaver process.
- [ ] I can write a short incident summary without exposing secrets.

## Next Steps

- NIST SP 800-63B: digital identity guidelines, authenticator assurance, and
  password guidance.
- OWASP Application Security Verification Standard: authentication, session
  management, and access control chapters.
- OAuth 2.0 Security Best Current Practice: redirect URI, `state`, PKCE, and
  token handling.
- CIS Controls v8: account management, access control, and continuous
  vulnerability management.
- Your organisation's access-review and offboarding procedures. A lab teaches
  the idea; the procedure is what makes it happen every time.
