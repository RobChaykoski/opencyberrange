# Setup and onboarding (frontend)

## Purpose

Guide a new deployment from first boot to a usable platform: create the first
administrator, choose security settings, enable modules, and review the choices.
Also host the privacy and usage pages that explain what the platform collects.

## Routes and views

| Route | View | Notes |
|---|---|---|
| `/setup` | `Setup.vue` | four-step wizard: account, security, modules, review |
| `/privacy` | `Privacy.vue` | privacy controls |
| `/youth-privacy` | `YouthPrivacy.vue` | under-18 safeguards |
| `/usage` | `Usage.vue` | public usage page |
| `/about` | `About.vue` | about and inventory |
| `/accessibility` | `About.vue` (tab) | accessibility position |

## API calls

| Action | Endpoint |
|---|---|
| Setup status | `GET /api/setup/status` |
| Create first admin | `POST /api/setup/complete` |
| Public config | `GET /api/public/config` |
| Privacy settings | `GET/PUT /api/auth/settings` |
| Consent | `/api/consent/*` |

## Behaviour that matters

- **Setup token.** If `SETUP_TOKEN` is set, the wizard requires it. This prevents
  a stranger claiming the first admin between boot and setup.
- **One-time setup.** Once an admin exists, `/setup` is closed.
- **No default credentials.** There is no built-in admin password.
- **Privacy defaults.** New accounts are private: no scoreboard, no public
  certificates, no optional email.
- **Modules.** Optional modules are mounted by the backend registry; the wizard
  only enables what the edition supports.
- **Public pages.** The usage and privacy pages must be readable without an
  account where the edition allows it.

## Storage

Setup state is held in the backend. The browser does not persist a setup token
after completion. Remove `SETUP_TOKEN` from `platform/.env` and restart the
backend after setup.

## Run and test

```bash
cd platform/frontend
npm run dev
npm test
```

Backend coverage: `tests/test_setup_gate.py`, `tests/test_public_config_api.py`,
`tests/test_privacy.py`, `tests/test_feature_flags.py`.

## Extension checklist

- Add the step and the validation.
- Do not make setup repeatable after the first admin exists.
- Do not ship a default password.
- Add a test for an unauthenticated setup attempt and a second setup attempt.
- Update the privacy notice if the step collects a new field.
- Remove the setup token from the environment after completion.

## Related

- [Local development](../../../local-development.md)
- [Backend roles and admin](../../../backend/features/roles-and-admin/README.md)
- [Privacy notice](../../../../docs/PRIVACY-NOTICE.md)
- [Minor-safe defaults](../../../../docs/MINOR-SAFE-DEFAULTS.md)
