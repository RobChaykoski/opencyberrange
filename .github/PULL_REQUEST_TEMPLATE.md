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

- [ ] No real credentials, personal data, or live targets added
- [ ] New lab content is fictional and isolated
- [ ] Authorization checks added or preserved on new endpoints
- [ ] `pip-audit` / `npm audit` still clean, or the exception is documented

## Notes for reviewers

<!-- Migration steps, screenshots, follow-up issues, or accepted risk. -->
