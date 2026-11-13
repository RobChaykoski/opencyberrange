# Wiki origin split

Status: **implemented for Release 4 deployments that set the split variables.**
The same-origin fallback (opaque sandbox plus an HttpOnly wiki cookie) remains
for deployments without a second hostname that points at the same instance.

## Why

The workbook iframe used to be same-origin with the SPA. Any script in the wiki
could read the SPA's `localStorage`, and the `wiki_auth` cookie was
JavaScript-set. The interim fix sandboxed the frame into an opaque origin, but
that required `SameSite=None` and still left the wiki served from the app
origin.

The split gives the wiki its own origin. The SPA keeps its token in
`localStorage`; the wiki gets an HttpOnly cookie and never receives a
JavaScript-readable copy.

## Design

| Piece | Value |
|---|---|
| App origin | `https://ctfd.example.edu` |
| Wiki origin | `https://ocr.example.edu` |
| Wiki cookie | `wiki_session`, HttpOnly, Secure, `SameSite=None`, `Domain=.example.edu` |
| Frame policy | wiki CSP `frame-ancestors 'self' https://ctfd.example.edu` |
| Auth check | nginx `auth_request` forwards `wiki_session` to the backend |

Both hostnames must resolve to the **same deployment** (the same frontend,
backend, database, and wiki volume). The browser treats them as different
origins because the hostnames differ. A hostname that points at a different
instance will authenticate against the wrong data and must not be used for the
split.

Flow:

1. The SPA calls `POST /api/auth/wiki-cookie` after login and on app load. The
   backend copies the bearer JWT into the HttpOnly `wiki_session` cookie.
2. The workbook iframe loads `https://ocr.example.edu/wiki/...`.
3. nginx validates `wiki_session` for the HTML and every subresource. The wiki
   scripts can run normally, including Mermaid and PDF export.
4. The framed page cannot read the parent's `localStorage`; it also cannot read
   `wiki_session` because the cookie is HttpOnly.
5. Logout calls `DELETE /api/auth/wiki-cookie` and clears the legacy
   `wiki_auth` cookie.

The API continues to authenticate from the bearer token. It does not accept
`wiki_session` as a general API credential.

## Configuration

### Frontend build

```env
# Empty keeps the wiki same-origin.
WIKI_BASE_URL=https://ocr.example.edu
```

This becomes `VITE_WIKI_BASE_URL` at build time.

### Frontend runtime

```env
# The app origin allowed to frame the wiki.
WIKI_FRAME_ANCESTOR=https://ctfd.example.edu
```

The container entrypoint substitutes this into the generated wiki CSP and
removes the literal placeholder. Leave it empty for a same-origin install.

### Backend runtime

```env
# Parent-domain scope for the HttpOnly wiki cookie.
WIKI_COOKIE_DOMAIN=.example.edu
```

Leave empty for a same-origin install; the cookie then stays host-only.

## DNS and TLS

Both hostnames must resolve to the frontend and have a valid certificate for
the browser. On the SWOCTS deployment:

- app: `ctfd.swocts.com` (Let's Encrypt)
- wiki: `ocr.swocts.com` (Let's Encrypt)

No additional port or service is needed. The frontend already serves any host.

## Verification

1. Log in on the app origin and open a workbook.
2. Confirm the iframe URL starts with `https://ocr.example.edu/wiki/`.
3. In the frame console:
   - `window.origin` is `https://ocr.example.edu`, not the app origin.
   - `window.parent.localStorage` throws `SecurityError`.
   - `document.cookie` does not expose `wiki_session`.
4. Mermaid renders and **Save as PDF** downloads.
5. The wiki response has `frame-ancestors` containing the app origin and no
   `X-Frame-Options` header.
6. Log out and confirm `wiki_session` is gone.

## Fallback

With `WIKI_BASE_URL` empty, the iframe stays same-origin but is sandboxed
without `allow-same-origin`. That is the development/backup path, not the
production security boundary. The split is the supported design for
internet-facing deployments.
