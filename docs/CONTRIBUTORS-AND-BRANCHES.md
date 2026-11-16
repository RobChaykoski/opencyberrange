# Contributors, branches, and licensing

## Maintainership

| Role | Person / entity |
|---|---|
| Current maintainer and release operator | Robert Chaykoski |
| Upstream OpenCyberRange/OCR-Lite author | Lewis Heuermann |
| Brand and crest | SWOCTS; designed by Avery Chaykoski |
| AI assistance | Disclosed in `BUILD_NOTICE.md` and `CONTRIBUTING.md`; a human maintainer remains responsible for every change |

The git history is the authoritative contributor record. Do not add a name to a
release document without that person's consent.

## Branches and remotes

| Ref | Purpose | Status |
|---|---|---|
| `main` | Canonical development and release branch | active |
| `canonical/main` on production | Fast-forward source for production | active |
| `backup` remote | Mirror of the production tree | mirror |
| `v2` remote | Historical v2 line | historical |
| `v5.17.1` | Signed current release tag | current |
| `v5.17.0` | Previous signed feature release | historical |
| `v5.0.0`–`v5.16.0` | Signed previous release tags | historical |
| `v2.7.0` | Unsigned historical tag (documented exception) | historical |

Release tags are signed with the release key fingerprint recorded in
[`RELEASES.md`](RELEASES.md) and [`SUPPLY-CHAIN.md`](SUPPLY-CHAIN.md). Do not
move a release tag after publication unless a release-blocking metadata defect
requires it; record the move in the deployment statement.

## Licensing and CLA

- The platform source and original content use the **PolyForm Noncommercial
  License 1.0.0**. See [`LICENSE`](../LICENSE), [`LICENSING.md`](../LICENSING.md),
  and [`BUILD_NOTICE.md`](../BUILD_NOTICE.md).
- Third-party components keep their own licences. See
  [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
- External **code** contributions require the CLA in
  [`.github/CLA.md`](../.github/CLA.md). The CLA allows the maintainer to use,
  modify, distribute, and sublicense the contribution, including in a commercial
  Enterprise edition, while the contributor keeps copyright.
- The CLA does not relicense the public Lite edition. A commercial deployment
  needs a separate commercial agreement; the public PolyForm licence is not a
  commercial licence.
- Do not merge a code contribution without a signed CLA. Documentation and
  issue reports do not require the CLA unless they include code.

## Review expectations

- Security-sensitive changes require the security delta review.
- A new route requires an authorization dependency and a regression test.
- A new lab requires the metadata contract, a competency contract, a workbook
  or explicit no-workbook decision, and a validation run.
- A new release requires a signed tag, a supply-chain lock, a backup, a restore
  drill, and the production deployment statement.
