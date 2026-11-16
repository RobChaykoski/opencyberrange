# Public homepage source marker (internal note)

The OSINT exercise **The Public Homepage** uses a reviewed offline mirror at
`platform/labs/OSINT/_shared/mirrors/swocts-public-homepage.html`. The mirror is
the assessed target and contains the marker:

```text
OCR{swocts_v13w_s0urc3}
```

The live page at `https://www.swocts.com` is an optional, read-only adult
extension. Do not modify a third-party site, add a tag to it, or contact its
owners as part of a lab. If the live page is used, only read the public source
and never collect personal data.

The offline mirror is the source of truth for the flag and the automated check.
If the mirror changes, update its SHA-256 in
`platform/backend/app/data/external-targets.yaml` and run
`python scripts/check-external-targets.py --offline`.
