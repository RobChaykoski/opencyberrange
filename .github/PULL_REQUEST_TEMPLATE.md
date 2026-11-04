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
- [ ] No real credentials, personal data, or live targets added
- [ ] New lab content is fictional and isolated
- [ ] Authorization checks added or preserved on new endpoints, with allowed/denied tests
- [ ] New rich text/markdown is sanitized and has an XSS regression test
- [ ] New personal data is covered by export, erasure, and retention notes
- [ ] Security-relevant actions emit an audit or activity event
- [ ] `pip-audit` / `npm audit` still clean, or the exception is documented with owner and expiry

## Notes for reviewers

<!-- Migration steps, screenshots, follow-up issues, or accepted risk. -->
