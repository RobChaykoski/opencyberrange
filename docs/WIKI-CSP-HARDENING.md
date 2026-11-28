# Wiki CSP hardening

Status: **design, not implemented.** RB-06 remains partial until the hash
pipeline ships.

## Problem

The generated wiki locations send:

```
script-src 'self' 'unsafe-inline'
style-src  'self' 'unsafe-inline'
```

`unsafe-inline` in `script-src` removes most of the protection a CSP provides.
The wiki is same-origin with the application on a normal install, so an
injection in generated content runs with the user's session.

The generator comment says a nonce or hash scheme "would need the site builder
to stamp each page". That is true for per-page nonces, but not for hashes: the
inline scripts are build output, so their hashes can be computed after the
build and emitted into the same generated nginx blocks.

## Measured

Built two sites with the current toolchain (`mkdocs 1.6.1`, Material 9.8.0):

| Site | Pages | Distinct inline-script hashes | Inline event handlers |
|---|---|---|---|
| `mkdocs-manual-lite.yml` | 122 | 10 | 0 |
| `mkdocs-webpt.yml` | 334 | 10 | 0 |

The union across both sites is **14 hashes**, with 6 shared. The count is small
enough for a single server-level list, and no page uses `onclick`/`on*`
attributes, so there is no second inline vector to account for.

## Option A — build-time hash list (recommended)

1. After `mkdocs build` for every site, walk the HTML, collect the text of each
   `<script>` without `src`, and sha256 it.
2. Union the hashes and emit `script-src 'self' 'sha256-…' …` into the
   generated wiki CSP in `tools/wiki-gen/generate.py` and the committed
   `platform/frontend/nginx-ssl.conf`.
3. Add a `--check` mode that rebuilds one representative site and fails when
   the committed hash list differs, mirroring `scripts/check-csp-hash.py` for
   the SPA.
4. Keep `style-src 'unsafe-inline'`: Material emits inline styles on nearly
   every element, and styles cannot execute script. Track that as the residual
   risk rather than pretending it is gone.

Cost: one build pass in CI, a generated hash block about 14–30 entries long.
Risk: a Material upgrade changes hashes; the `--check` gate makes that a
deliberate update rather than a silent break. If the hash list is wrong, pages
fail closed (scripts blocked), which is visible immediately.

## Option B — separate origin

Serve the wiki from its own hostname (the `:8443` workbook origin already
demonstrates the pattern) instead of a path on the app origin. `frame-ancestors`
then controls embedding, and an injection in wiki content cannot read the
application's cookies or storage.

Cost: DNS/TLS for a second name, a deployment change, and a migration note for
institutions that hard-code URLs. This is the stronger boundary and the right
end state for internet-facing multi-tenant installs, but it is an operational
change, not just a config edit.

## Recommendation

Ship Option A first: it removes `unsafe-inline` from `script-src` with no
deployment change and a CI gate. Then evaluate Option B for institutions that
run the wiki on a public hostname. Until A ships, the current CSP is honest but
weak, and `docs/TRACKED-EXCEPTIONS.md` keeps RB-06 partial.

## Validation checklist for the implementation

- [ ] Hash collector runs after every site build, not per page.
- [ ] Generated and committed CSP match; `--check` fails on drift.
- [ ] A page with a deliberately modified inline script is blocked in a browser.
- [ ] `style-src` residual documented with the Material upgrade path.
- [ ] No inline event handlers in any generated page (currently 0).
