# Language and localization

Status: **English-only UI for 5.36; French UI chrome and localized email/PDF
are a Release 6 wave.** This page is the scope contract, not a promise that the
current UI is translated.

## Three layers, three different answers

| Layer | Examples | Decision |
|---|---|---|
| **UI chrome** | Buttons, labels, menus, validation text, empty states | `vue-i18n` and locale catalogues. Baseline gate now; French wave in Release 6 |
| **Backend-generated text** | Emails, PDF exports, security-event descriptions | Resolve the recipient's locale per request; small `app/locales/` tree. Not a global translation system |
| **Course, lab, and workbook content** | Scenarios, walkthroughs, hints, analysis questions | Per-language MkDocs builds and authored editions. Never put curriculum prose in UI locale JSON |

Mixing curriculum content into the UI translation files is the trap. Authored
content is deep, versioned, and reviewed; it belongs in the MkDocs/manifest
pipeline.

## What ships now

- **Bare-string baseline gate.** `vue/no-bare-strings-in-template` is enabled as
  a warning. `platform/frontend/scripts/check-ui-strings.mjs` records the
  current 4,943 bare strings across 96 files in
  `platform/frontend/scripts/ui-string-baseline.json`. CI fails when a file
  grows beyond its baseline or the total grows. There is no requirement to
  translate the whole UI in one release; there is a requirement not to make the
  backlog larger.
- **Stable API error codes.** New and migrated endpoints add an
  `X-Error-Code` header alongside the existing human-readable `detail`. See
  [API error codes](API-ERROR-CODES.md).
- **Terminology seed.** `curriculum-glossary.yaml` is the glossary translators
  should use for cybersecurity terms. Machine translation without it will
  produce confident nonsense.
- **Scope line.** Release 6 carries the localization wave; it is not an
  unstated assumption.

## The gate in practice

```bash
cd platform/frontend
npm run check:i18n              # fail on new bare strings
node scripts/check-ui-strings.mjs --update   # only for a reviewed baseline change
```

When you touch a file, move its new strings into the locale catalogue and lower
that file's baseline. Do not raise the baseline to make a feature fit.

## Release 6 wave

| Item | Scope | Gate |
|---|---|---|
| UI chrome | Extract strings to namespaced locale files; add French; negotiate stored preference -> `Accept-Language` -> `en` | No bare-string growth; `fr` catalogue covers every extracted key; keyboard and screen-reader pass |
| Formatting | `Intl.DateTimeFormat`, `Intl.NumberFormat`, and `Intl.RelativeTimeFormat` using the resolved locale | Dates, numbers, and counts match the locale in both themes |
| Email and PDF | Resolve the recipient's locale; translate the small server-side catalogue | A French recipient receives a French email and PDF with the same facts |
| Docs | One locale per MkDocs build (`mkdocs-fr-*.yml`) into `wiki/fr/...`; keep the source single-language per author | `wikiAuth` still gates each path; no mixed-language navigation |
| RTL groundwork | Prefer CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline`) over `left`/`right` | A `dir="rtl"` smoke page does not break layout |
| Translation workflow | Weblate (self-hosted, Git-native) or an equivalent with translation memory | Translators never edit Vite or application code; strings stay in the repo |

## Rules

- English-first is a **documented scope**, not an accident. A missing translation
  is a known gap, not a bug report.
- Do not machine-translate public-facing course content. If machine translation
  is used for an internal draft, human review gates publication.
- Do not add a second theme, a parallel CSS system, or a locale-specific layout.
  The existing tokens and components remain the source of truth.
- Do not put flags, credentials, or learner PII in a translation string.
- Keep the glossary current before a translation wave. A term with two meanings
  in two languages is worse than an untranslated term.

## Related

- [API error codes](API-ERROR-CODES.md)
- [Release 6 scope](RELEASE-6-SCOPE.md)
- [`curriculum-glossary.yaml`](../curriculum-glossary.yaml)
- [Design system](../.opencode/skills/opencyberrange-design/references/design-system.md)
