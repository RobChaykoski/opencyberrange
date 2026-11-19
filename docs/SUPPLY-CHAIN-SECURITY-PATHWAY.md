# Supply chain security pathway

Status: **proposal** (18 November 2026).

Supply chain is not entirely missing from the roadmap. The platform has a
supply-chain lock, signed releases, and four DevSecOps exercises:

- `web-11-6-devsecops-pipeline`
- `web-11-7-container-security`
- `web-11-8-kubernetes-security`
- `web-11-9-supply-chain-integrity`

What is missing is a dedicated learner pathway that starts with a malicious
package and ends with a verified, reproducible build. This proposal turns the
existing AppSec coverage into a standalone five-lab sequence with evidence.

## 1. Why this pathway

Most graduates can describe a dependency and run a scanner. Fewer can:

- read a lockfile and explain why a transitive package changed;
- detect a typosquat or dependency-confusion package before install;
- pin and verify a CI action;
- generate and consume an SBOM;
- verify an artifact signature and provenance attestation;
- contain a compromised build without deleting the evidence;
- explain the business impact to a release manager.

Those are the tasks a DevSecOps or platform-security team actually assigns.

## 2. Outcomes

By the end of the pathway a learner can:

- identify direct, transitive, and development-only dependencies;
- detect typosquatting, dependency confusion, and install-script abuse;
- pin and verify CI actions and container images;
- generate CycloneDX and SPDX SBOMs and scan them for known vulnerabilities;
- verify a signature and provenance attestation before deployment;
- design a build pipeline with least privilege, isolation, and provenance;
- respond to a poisoned dependency or build with a timeline and evidence;
- explain release risk to a product owner without overstating certainty.

## 3. Lab sequence

### Lab 1 — The typo that installs a backdoor

A project adds a package whose name is one character away from a popular
library. The package runs a post-install script that reads environment
variables and writes a synthetic beacon configuration.

Learner tasks:

1. Compare the package name, publisher, repository, and release history.
2. Inspect `package.json`, the lockfile, and the install scripts.
3. Confirm the package is not the intended dependency.
4. Remove it, regenerate the lockfile, and add a registry allowlist or
   dependency policy.
5. Add a CI check that fails on an unexpected package source.

Evidence: dependency diff, install-script excerpt, fixed lockfile, CI check.

### Lab 2 — The compromised GitHub Action

A workflow uses a third-party action by a mutable tag. The action is replaced
with a version that prints a synthetic token to the log and posts it to a lab
collector.

Learner tasks:

1. Review the workflow for unpinned actions and excessive `GITHUB_TOKEN`
   permissions.
2. Identify the action revision that changed.
3. Pin the action by commit SHA and reduce permissions to `contents: read`.
4. Add a policy check that rejects mutable tags.
5. Rotate the synthetic token and confirm the old one is rejected.

Evidence: workflow diff, permission diff, policy check, rotation record.

### Lab 3 — The public package that shadows the private one

A build resolves `@company/internal-lib` from the public registry because the
private registry is not scoped. A public package with the same name runs a
malicious preinstall script.

Learner tasks:

1. Reproduce the resolution path.
2. Show which registry and version won.
3. Scope the private registry and pin the expected package.
4. Add a lockfile integrity check and a registry allowlist.
5. Write a short explanation of dependency confusion for a release manager.

Evidence: resolution trace, registry configuration, fixed lockfile, note.

### Lab 4 — SBOM and vulnerability triage

A container image contains a mix of direct and transitive dependencies. The
learner generates an SBOM, scans it, and prioritises the findings.

Learner tasks:

1. Generate a CycloneDX SBOM and an SPDX SBOM.
2. Compare the package inventory with the image contents.
3. Scan for known vulnerabilities and identify reachable versus unreachable
   components.
4. Prioritise using severity, exploitability, and exposure.
5. Record the accepted risk and the review date.

Evidence: SBOM files, scan output, triage table, risk decision.

### Lab 5 — Signature, provenance, and the poisoned build

A build artifact is signed but the provenance attestation shows it was built
from a different commit than the one in the release note. The learner must stop
the release, preserve evidence, and fix the pipeline.

Learner tasks:

1. Verify the artifact signature and the provenance attestation.
2. Compare the attested source, builder, and commit with the release record.
3. Identify the pipeline step that allowed the substitution.
4. Contain the artifact and revoke the signing identity if needed.
5. Harden the pipeline: isolated builder, least-privilege token, required
   provenance, and a release gate.
6. Write the incident timeline and the executive summary.

Evidence: signature verification, provenance diff, containment record, fixed
pipeline, reports.

## 4. Tools

| Tool | Use |
|---|---|
| **Syft** | Generate SBOMs from images, filesystems, and archives |
| **Grype** | Scan SBOMs and images for vulnerabilities |
| **Trivy** | Image, filesystem, and configuration scanning |
| **Cosign / Sigstore** | Sign and verify artifacts and attestations |
| **OpenSSF Scorecard** | Assess dependency and repository hygiene |
| **Dependency-Track** | Inventory and policy for SBOMs |
| **npm / pnpm / pip** | Show lockfile and registry resolution behaviour |
| **GitHub Actions or a local runner** | Demonstrate workflow permissions and pinning |

The labs can run entirely with local registries and synthetic packages. Do not
publish a malicious package to a public registry.

## 5. Safety

- Never upload a malicious package to npm, PyPI, or any public registry.
- Keep the synthetic package and collector inside the lab network.
- Use fake tokens and fake registry credentials.
- Do not run an untrusted install script on a shared host; use an isolated
  container with no egress and a read-only workspace.
- Do not include real customer data in the SBOM or scan output.
- Do not present the capstone as a real vulnerability disclosure.

## 6. Assessment

Each lab requires a flag plus one artifact. The capstone requires a timeline,
a containment record, and an executive summary. The learner is assessed on:

- accuracy of dependency and provenance analysis;
- quality of the evidence;
- whether the fix addresses the root cause, not only the symptom;
- clarity of the release-risk explanation;
- safe handling of the synthetic malicious artifact.

## 7. Mapping to employer gaps

| Gap | Labs |
|---|---|
| Cloud security operations | 5 |
| Detection engineering | 2, 5 |
| Threat hunting | 2, 5 |
| Incident response | 5 |
| Identity and access management | 2 |
| Security automation | 1, 3, 4, 5 |
| Vulnerability management | 4 |
| Security architecture | 3, 5 |
| GRC and compliance | 4, 5 |
| Communication | 3, 5 |

## 8. Achievements

- **Dependency Detective** — labs 1 and 3.
- **Pipeline Guardian** — lab 2.
- **SBOM Analyst** — lab 4.
- **Provenance Verifier** — lab 5.
- **Supply Chain Defender** — all five labs.

Use the existing `tracks` group with gold and platinum tiers.

## 9. Implementation phases

1. **Phase 1 — dependency labs.** Build the synthetic package, local collector,
   and npm/pip resolution exercises.
2. **Phase 2 — pipeline lab.** Add a local workflow runner or a documented
   GitHub Actions exercise with a lab repository.
3. **Phase 3 — SBOM labs.** Add Syft, Grype, and Trivy to the RangeBox or a
   dedicated tool container.
4. **Phase 4 — provenance capstone.** Add Cosign, a local registry, and a
   release-gate exercise.

## 10. Acceptance criteria

- All labs run without public registry access.
- No malicious package is published outside the lab.
- Every lab produces a flag and an evidence artifact.
- The capstone requires a root-cause fix and a report.
- The pathway can be completed in the existing RangeBox or a documented tool
  container.
- The mapping to at least one framework or employer gap is visible in the
  workbook.
