# Software Security — Chapter Review

## What You Practised

- Reading shipped JavaScript instead of trusting the visible page
- Finding a hidden route and a client-side token
- Explaining why client-side checks are not authorization
- Recognising untrusted input flowing into a shell
- Using a command separator to read a flag
- Explaining the fix with argument arrays and allowlisting

## Self-Assessment

Rate each statement from 1 (not yet) to 5 (confident):

- [ ] I can explain why front-end code is public.
- [ ] I can find a route or token in a JavaScript bundle.
- [ ] I can explain why a hidden admin link is not access control.
- [ ] I can identify a shell-injection point in a small function.
- [ ] I can explain why `shell=False` with an argument list is safer.
- [ ] I can describe one test that would catch each bug.

## Answer Key

### Hidden Export Route

- The route was `/admin/export?token=devfest-export-2026`.
- The token was in `/static/app.js`.
- The bug is broken access control: the server trusted a token that every
  visitor could read.
- The fix is server-side authorization, not a better-hidden link.

### Diagnostics Command Injection

- The host field reached a shell command.
- `;` separated the lookup from `cat /tmp/flag`.
- The fix is an argument array with `shell=False`, plus input validation and
  least privilege.

## Remediation Checklist

- [ ] Remove secrets and temporary admin routes from front-end bundles.
- [ ] Enforce authorization on the server for every route.
- [ ] Replace string-built shell commands with argument arrays.
- [ ] Allowlist expected hostnames, IPs, or formats.
- [ ] Run services as unprivileged users with dropped capabilities.
- [ ] Add negative tests for unauthenticated and injected requests.
- [ ] Review dependencies and error messages for leaked internals.

## Next Steps

- Level 3: authentication and authorization flaws.
- Level 4: memory safety and a first exploit script in a RangeBox.
- Level 5: an end-to-end capstone with a written disclosure.

If you are joining the DevFest competition, you can attempt the challenges in
any order. The leaderboard uses the same flag and scoring rules as the rest of
the platform.

## Free practice and certification next steps

These optional free resources match this chapter. They do not replace the
lab or this workbook.

- **PortSwigger Web Security Academy** — free secure-coding and web-security labs: <https://portswigger.net/web-security>
- **Linux Foundation training** — free open-source security courses: <https://training.linuxfoundation.org/resources/>
- **ISC2 Certified in Cybersecurity** — free entry-level training and exam pathway: <https://www.isc2.org/landing/1mcc>

See [Free training and certifications](../FREE-TRAINING-AND-CERTIFICATIONS.md)
for the full map and the privacy note.
