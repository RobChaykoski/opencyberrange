# Release 5.46.1 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.46.1` |
| Signed tag | `v5.46.1` |
| Release commit | Pending tag |
| Alembic | `0065_legacy_kali_columns` (no migration) |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |

## Design alignment

The panel was reviewed against the OpenCyberRange design skill at
`.opencode/skills/opencyberrange-design/SKILL.md` and its design-system,
accessibility, and frontend-convention references.

| Change | Reason |
|---|---|
| Token substitution | Replaced `--panel`, `--border`, `--muted`, and `--accent-soft` with `--bg-secondary`, `--border-color`, `--text-secondary`, `--accent-bg`, and `--warning-bg` |
| Sample notice | Uses `--warning-bg` and a text label, not colour alone |
| Progress semantics | Bars expose `role="progressbar"`, `aria-valuemin`, `aria-valuenow`, `aria-valuemax`, and a per-row label |
| Bar scale | Bars scale to the largest row for comparison; the percentage remains the share of reported entries |
| Empty state | Added a "no aggregated rows yet" message with the refresh path |
| Reading column | `1080px` with `minmax(0, 1fr)` grids to prevent overflow |
| Responsive | `640px` stacking rule and reduced page padding |
| Focus | Visible `2px` accent focus ring on links; decorative sidebar icon is `aria-hidden` |
| Motion | Explicit `prefers-reduced-motion` rule |

The three themes were checked by token inspection: dark (`:root`), light
(`[data-theme="light"]`), and high contrast. A real-browser visual pass is still
listed as unverified below.

## Verification

| Check | Result |
|---|---|
| Frontend build | Passed |
| Frontend tests | `37 passed` |
| i18n budget | `5,300` bare strings across `104` files (baseline updated in review) |
| Backend tests | Unchanged from 5.46.0: `1,189 passed` |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Development `/threat-awareness` | Pending |
| Production `/threat-awareness` | Pending |
| Production health | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Not verified

- A manual browser pass at `375`, `768`, `1024`, and `1440` px.
- A screenshot in the high-contrast theme.
- Screen-reader announcement order for the progress bars.

These are documented rather than claimed. The markup and tokens follow the
design references, but a human visual check is still required.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Panel reachable and styled on development and production.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Production drift still 48 operations.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
