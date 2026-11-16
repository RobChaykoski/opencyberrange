## Summary

<!-- What does this change and why? One short paragraph. -->

## Type

- [ ] Bug fix
- [ ] Security fix
- [ ] Lab or workbook content
- [ ] Platform feature
- [ ] Dependency or infrastructure upgrade
- [ ] Documentation

## Verification

<!-- Paste the commands you ran and their result. -->

- [ ] `pytest -q` (backend, PostgreSQL 17)
- [ ] `npm run lint` and `npm run build` (frontend)
- [ ] `python scripts/validate-lab.py <lab>` for changed labs
- [ ] Manually exercised the affected screen or endpoint

## Security checklist

- [ ] OWASP Top 10 categories touched are listed (see `docs/V2-SECURITY-OWASP-TOP-10.md`)
- [ ] No operational malware, real personal data, or unauthorised live targets added. Any live OSINT target has an inventory entry, an offline mirror, a content hash, and a read-only authorisation note
- [ ] New lab content is fictional and isolated
- [ ] Authorization checks added or preserved on new endpoints, with allowed/denied tests
- [ ] New rich text/markdown is sanitized and has an XSS regression test
- [ ] New personal data is covered by export, erasure, and retention notes
- [ ] Security-relevant actions emit an audit or activity event
- [ ] `pip-audit` / `npm audit` still clean, or the exception is documented with owner and expiry

## Documentation and privacy checklist

- [ ] Version, tag, and lab counts match `versions.yaml` and `docs/COUNTS.md`
- [ ] Links, images, the API manual, and the MkDocs strict build pass
- [ ] Screenshots use synthetic data, show the current release, and contain no personal data
- [ ] Historical content is archived or labelled; no stale "current" claim remains
- [ ] New personal data has export, erasure, and retention notes
- [ ] No secret, real learner data, or live target appears in examples, logs, or screenshots

## Notes for reviewers

<!-- Migration steps, screenshots, follow-up issues, or accepted risk. -->
