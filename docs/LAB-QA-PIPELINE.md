# Lab QA pipeline

The lab QA pipeline proves a lab starts, is isolated, is solvable, returns the
right flag, and matches its workbook. It complements the
[release test plan](RELEASE-TEST-PLAN.md).

## 1. What runs

| Stage | Tool | Proves |
|---|---|---|
| Contract | `validate-lab.py --all` | required metadata, flag format, compose, test steps |
| Manifest | `generate-lab-manifests.py --check` | tester contract is current |
| Static harness | `lab_harness.py --validate-all` | every manifest is structurally valid |
| Workbook | `lab_qa.py --static` | links, images, commands, IPs, flags, tools, path plans |
| Live startup | `lab_harness.py --lab <slug>` | build, start, health, ports, isolation, flag, repeat, resources, teardown |
| Live workbook | `lab_qa.py --live` | delegates to the live harness |
| Links | `check-links.py Workbook --mkdocs` | workbook navigation and relative links |
| Publication | `audit-publication.py --summary` | no answer keys or real data in public content |

## 2. Static pipeline

```bash
python scripts/validate-lab.py --all
python scripts/generate-lab-manifests.py --check
python scripts/lab_harness.py --validate-all
python scripts/lab_qa.py --static
python scripts/lab_qa.py --static --strict-flags   # after flag allowlist review
python scripts/check-links.py Workbook --mkdocs
python scripts/audit-publication.py --summary
```

`lab_qa.py --static` checks:

- the workbook link resolves to a page;
- every image exists, has alt text, and matches the reviewed hash baseline;
- every relative link target exists;
- URLs are HTTPS, no bare public IP, no unsafe scheme;
- public IPv4 addresses are flagged for review (documentation ranges, loopback, and lab literals are informational);
- `.lab` hostnames match `lab.yaml`;
- shell blocks parse with `bash -n`;
- no destructive command (`rm -rf /`, `mkfs`, `dd`, pipe-to-shell);
- no workbook flag, and no workbook flag that differs from `lab.yaml`;
- known tool versions are not below the reviewed minimum;
- a path plan exists (informational until the coverage gate is enabled).

## 3. Screenshot baseline

Screenshots cannot be verified by a static scan. The pipeline hashes them and
requires a human review date:

```bash
python scripts/lab_qa.py --write-screenshots
```

Then review each image and set `reviewed_at` and `lab_slug` in
`platform/tester/screenshots.yaml`. A changed image fails until it is reviewed
again. An unreviewed image is a warning.

The review asks:

- Is the screenshot from the current target version?
- Does it show the same UI, hostname, port, and account as the current lab?
- Is any secret, flag, token, or learner row visible? If yes, remove it.
- Is the image necessary? Prefer a command transcript over a screenshot.

## 4. Flag mismatch example

The failure this pipeline catches:

```text
Workbook says:  FLAG-ABC123
Container says: FLAG-ABC124
```

`lab_qa.py` reads every `OCR{...}` in the workbook and compares it to the
`flag` in `lab.yaml`. A difference is a warning by default so a stage marker or example can be
reviewed; --strict-flags turns it into an error once the reviewed allowlist is
settled. A match is always an error because the workbook must not expose the
answer. The live harness separately extracts
the flag from the solver output and compares it to the manifest/lab flag. A
flag that exists but cannot be obtained fails the live run.

## 5. Path and bypass validation

The intended path is proven by the live solver. Alternate paths need a review
plan because automation cannot know every shortcut.

Create `platform/tester/paths/<slug>.yaml`:

```yaml
lab_id: linux-3-1-suid-privilege-escalation
intended_path: >
  Find the misconfigured SUID binary, use it to read the protected file, and
  recover the flag through the intended privilege boundary.
bypass_checks:
  - name: kernel exploit
    command: >
      cd /tmp && ./kernel-exploit 2>/dev/null | grep -o 'OCR{[^}]*}'
    must_not_contain: "OCR{"
    rationale: >
      A kernel exploit would skip the SUID lesson even if it obtains the flag.
  - name: direct flag read
    command: "cat /root/flag 2>/dev/null"
    must_not_contain: "OCR{"
    rationale: The learner must cross the SUID boundary, not read the file directly.
```

The live review runs each `command` in the same lab network and fails if the
output contains the lab flag. Until the live bypass runner is wired into the
harness, record the manual result in the path file and the release evidence.
`lab_qa.py --static` validates the plan shape and reports coverage; it does not
execute the commands.

## 6. DNS and VPN

The live harness proves the tester sidecar can reach the declared services. It
does not prove the learner's WireGuard path. Add both:

- **DNS**: from the lab network, resolve the compose service names and the
  declared `*.lab` hostnames. Control-plane names must not resolve.
- **VPN**: two-peer drill. Each peer reaches only its own lab `/24`; the rest of
  `10.100.0.0/16`, the management LAN, the database, and the host are blocked.

See [Security validation](security/SECURITY-VALIDATION-PLAN.md#23-vpn-separation).

## 7. CI

Static checks run in the Quality workflow. Live checks run in the manual
Lab harness workflow on a self-hosted Docker runner, with a weekly canary and a
full release run. The release matrix is in
[`platform/tester/release-tests.yaml`](../platform/tester/release-tests.yaml).

```bash
python scripts/release_tests.py --automated-only
python scripts/release_tests.py --live --test lab-launch --test docker-isolation
```

## 8. Gate policy

Block the release when:

- a lab cannot start, becomes healthy, or expose its declared port;
- the flag is missing, unobtainable, or differs from `lab.yaml`;
- the workbook exposes or disagrees with the flag;
- a lab reaches the host, control plane, database, or another learner;
- a workbook image is missing, changed without review, or contains a secret;
- a path plan shows an alternate path that skips the learning objective.

Warnings are allowed with an owner and target date.

## Related

- [Release test plan](RELEASE-TEST-PLAN.md)
- [Lab runtime](../.onboarding-docs/lab-runtime/subsystem-overview.md)
- [Lab metadata schema](LAB-METADATA-SCHEMA.md)
- [Lab harness README](../platform/tester/README.md)
