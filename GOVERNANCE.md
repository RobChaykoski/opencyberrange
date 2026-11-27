# Governance

This page states how decisions are made for SWOCTS Cyber Range. It is short on
purpose; the [documentation standard](docs/documentation/DOCUMENTATION-STANDARDS.md)
and [CONTRIBUTING.md](CONTRIBUTING.md) cover the mechanics.

## Current model

SWOCTS Cyber Range is maintainer-led. The maintainer sets direction, reviews
every change, and signs every release. There is no elected committee.

| Role | Who | Decides |
|---|---|---|
| Maintainer | Robert Chaykoski | Roadmap, releases, security response, licence and commercial terms |
| Reviewers | Invited contributors | Scoped review in their area; the maintainer keeps the final merge |
| Contributors | Anyone | Proposals and pull requests; see [CONTRIBUTING.md](CONTRIBUTING.md) |

## How decisions are made

1. **Open a discussion or issue.** State the problem, the affected learners or
   operators, and the smallest change that solves it.
2. **Prefer the source of truth.** Proposals that disagree with the signed tag,
   `versions.yaml`, or `docs/COUNTS.md` must say which one changes and why.
3. **The maintainer decides.** Consensus is preferred; it is not required. The
   decision and its rationale are recorded in the issue or an ADR under
   `docs/decisions/`.
4. **Security is private.** A vulnerability goes through
   [SECURITY.md](SECURITY.md), never a public issue.

## Releases and the release chain

- Releases ship only as signed annotated tags, with a signed supply-chain lock
  and the stable integrity manifest. See [docs/RELEASES.md](docs/RELEASES.md).
- Changes to `supply-chain.lock.json`, its signature, the release key, the lock
  script, or `versions.yaml` require the maintainer's explicit review;
  `.github/CODEOWNERS` records that.
- The release key is held offline. Its rotation and revocation procedure is in
  [SECURITY.md](SECURITY.md#release-signing-key).

## Editions and commercial work

One codebase carries the Community / Academic, Professional, and Enterprise
profiles. The public tree is the Lite edition under PolyForm Noncommercial 1.0.0.

- Commercial editions, hosted deployments, and support contracts fund the work;
  they do not remove features from the public tree.
- Commercial requirements are prioritised through the contract, not by closing
  the public repository or accepting contributions under different terms.
- The maintainer keeps the right to relicense the work under the terms of the
  [CLA](.github/CLA.md). The upstream attribution and Required Notice stay in
  force; see [BUILD_NOTICE.md](BUILD_NOTICE.md).

## Contributions

- Code contributions require a signed CLA before merge.
- Curriculum and documentation contributions follow the same review and the
  same licence as the project.
- The [Code of Conduct](CODE_OF_CONDUCT.md) applies to every space.

## Changing this page

Open a pull request. Governance changes need the maintainer's approval and are
recorded in the changelog when they change contributor expectations.
