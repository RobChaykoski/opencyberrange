# Lab Definitions Repository (OpenCyberRange-Labs)

Status: **proposal** (18 November 2026). A separate, MIT-licensed repository for
labs-as-code. The platform repository stays under its existing licence.

## 1. Why a separate repository

- **Licensing clarity.** Lab definitions, synthetic datasets, and runtime
  templates can be MIT while the platform remains PolyForm Noncommercial.
- **Contribution flow.** Educators and practitioners can contribute a lab
  without learning the whole application.
- **Release cadence.** Labs can ship on their own schedule.
- **Supply chain.** The platform consumes signed, pinned lab releases instead of
  executing whatever is on `main`.
- **Reuse.** The same lab package can run under Compose, Kubernetes, or a future
  federation target.

## 2. Scope

In scope:

- `lab.yaml` metadata and learning design;
- Docker Compose, Kubernetes, Terraform/OpenTofu, and Ansible templates;
- synthetic datasets and mock services;
- validation, packaging, and release tooling;
- references to public standards and original practice content.

Out of scope:

- copyrighted course content, exam dumps, or vendor training material;
- real malware, real patient data, real credentials, or production data;
- the platform application code;
- a hosted lab service or cloud account.

## 3. Repository layout

```text
opencyberrange-labs/
  LICENSE                       MIT
  README.md
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  SECURITY.md
  catalogue.yaml
  schemas/
    lab.schema.json
    runtime.schema.json
  labs/
    <track>/
      <lab-slug>/
        lab.yaml
        README.md
        workbook/               # optional Markdown source
        compose/
          docker-compose.yml
        k8s/
          manifests/
        tofu/
          main.tf
        ansible/
          playbook.yml
        data/
          synthetic/
        tests/
          smoke.md
        PROVENANCE.md
  packages/
  scripts/
    validate.py
    package.py
    sign.py
  .github/workflows/
    validate.yml
    release.yml
```

## 4. Lab contract

Reuse the existing [lab metadata schema](LAB-METADATA-SCHEMA.md) so the platform
does not need a second format. Add package-level fields:

```yaml
id: sentinel-threat-hunting
slug: sentinel-threat-hunting
version: 0.1.0
license: MIT
content_version: "2027.1"
reviewed_at: "2026-11-18"
review_status: "static validation; live run pending"
runtime:
  compose: compose/docker-compose.yml
  kubernetes: k8s/manifests
  tofu: tofu
  ansible: ansible/playbook.yml
resources:
  cpu: 0.5
  memory: 512M
  pids: 256
safety:
  real_malware: false
  real_pii: false
  outbound_network: false
  privileged: false
provenance:
  author: "Contributor name"
  sources:
    - label: "NIST SP 800-61r2"
      url: "https://csrc.nist.gov/pubs/sp/800/61/r2/final"
  asset_licenses:
    - "Synthetic data generated for this lab"
```

A lab without a competency mapping, safety declaration, provenance, and
validation result is not releasable.

## 5. Runtime templates

Each lab declares one or more runtime targets:

| Target | Use | Minimum validation |
|---|---|---|
| Compose | Local RangeBox and single-host labs | `docker compose config`, smoke run |
| Kubernetes | k3s/kind labs | schema validation, `kubectl apply --dry-run=server`, policy check |
| OpenTofu/Terraform | Cloud-like or infrastructure labs | `tofu fmt -check`, `tofu validate`, plan |
| Ansible | Configuration and hardening labs | `ansible-lint`, syntax check |

The platform must not execute a runtime template from an untrusted pull request.
Only signed releases can be promoted.

## 6. Datasets

- Synthetic only. No real PII, patient data, or customer data.
- State the generation method and the licence.
- Keep files small; use download references for large captures.
- No real malware. Use harmless test artifacts, hashes, or a documented
  out-of-band sample process with governance.
- Include a manifest with SHA256 hashes.
- Include a cleanup/reset note.

## 7. Validation pipeline

The CI gate must run:

1. JSON Schema validation for `lab.yaml` and `runtime`.
2. Competency and framework mapping check.
3. Learning-outcome quality check (observable verbs, 3–5 outcomes).
4. Safety check: no privileged mode, host mounts, real malware, PII, secrets, or
   outbound network.
5. Runtime validation for every declared target.
6. Compose/Kubernetes policy check.
7. Secret scan and dependency scan.
8. Link check for references.
9. Markdown/MkDocs build if the workbook is included.
10. Package build and checksum.

A warning is allowed only when the reviewer records a reason.

## 8. Release and platform integration

- Semantic version per lab and one catalogue version per release.
- Signed Git tag and a signed manifest with SHA256 for every file.
- Package as a tarball or OCI artifact; publish the checksum and signature.
- The platform pins a release tag, not `main`.
- The admin import flow reads the package, validates it again, and imports the
  lab as a draft.
- A lab update is a new version; never mutate a published version.
- The platform stores the source release, version, and checksum with the lab.

Do not let the platform auto-run a remote repository's Terraform, Ansible, or
shell scripts on import. Import is a review step.

## 9. Governance

- Maintainers review for learning design, safety, and technical correctness.
- Two reviewers for a new track or a lab with a privileged/networked runtime.
- An industry reviewer for role alignment where possible.
- A monthly catalogue review and an annual licence/provenance audit.
- Contributors agree to the MIT licence and the provenance policy.
- A code of conduct applies to issues, reviews, and lab content.

## 10. Migration from the current repository

1. Freeze the current `platform/labs` tree as the source of truth.
2. Copy one track into the new repository without changing behaviour.
3. Add the schema, provenance, and validation.
4. Publish a signed `v0.1.0` release.
5. Point a development platform at the package and import one lab.
6. Compare the imported lab with the in-tree version.
7. Migrate track by track; keep the in-tree fallback until the package path is
   proven.
8. Remove the in-tree copy only after a full release passes the same tests.

## 11. Acceptance criteria

- The repository has an MIT licence and a provenance policy.
- Every lab validates against the shared schema.
- Every lab declares runtime targets, resources, safety, and provenance.
- No real malware, PII, secret, or copyrighted content is present.
- A signed release is reproducible from the tag.
- The platform imports a pinned release as a draft.
- A lab update does not mutate an existing version.
- The in-tree labs remain usable until the migration is complete.
