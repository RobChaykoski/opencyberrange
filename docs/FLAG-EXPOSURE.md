# Flag exposure

Status: **audit and answer-leak gate in place; static-flag migration not
started.**

Flags are the graded answers for a lab. The platform must know them, but a
learner must not be able to read them from the public repository before class.
This page records the current exposure and the plan to close it.

## How flags work today

- **222 labs.** **136** labs rotate per session: 75 environment-driven labs match a
  `FLAG` / `*_FLAG` compose value to the graded hash, and 61 baked labs declare a
  render contract. **86** labs keep a static value. Their flag is written in
  `lab.yaml`, and often again in the compose environment or the lab source. That
  value is public.
- A render contract has two modes. `write` (default) writes the flag file.
  `replace` swaps the static value inside an existing report, log, or history
  file, so the surrounding content survives.
- Baked labs can declare `flag_path`, `flag_service`, `flag_command`, and
  `flag_owner`. The launcher writes `LAB_FLAG`, sets ownership, and execs the
  original command.

## Audit

`scripts/audit_flag_exposure.py` separates three things:

- static declarations in `platform/labs/**` (expected, but public);
- template and demo values, such as a `token1_token2` placeholder or `demo`;
- **leaked answers**: a public file outside the lab tree that repeats a static
  lab flag.

Run it before a release or after a lab change:

```bash
python scripts/audit_flag_exposure.py
python scripts/audit_flag_exposure.py --fail-on-leaks
```

Current result: **96 static labs**, **0 leaked answers** outside the lab tree.
The Workbook capstone page that printed a real marker was replaced with a
read-the-route instruction. The rotation batches so far:

**Batch 1:** `linux-1-6-version-vulnerability-identification`,
`web-1-2-technology-identification`, `web-1-6-comprehensive-web-reconnaissance`,
`windows-2-3-smb-anonymous-share-access`, `malware-1-1-eicar-triage`.

**Batch 2:** `windows-1-1-basic-port-scan`,
`windows-2-4-smb-file-retrieval`, `windows-3-1-smb-manual-credential-test`,
`windows-3-2-smb-multiple-credential-testing`,
`windows-3-3-smb-single-user-brute-force`,
`windows-3-4-smb-username-enumeration-and-brute-force`.

**Batch 3 (replace mode):** `linux-2-2-ssh-user-discovery`,
`linux-2-5-ssh-history-analysis`, `malware-2-2-yara-fundamentals`,
`malware-2-3-yara-incident-triage`.

**Batch 4:** `web-1-3-http-methods-enumeration`,
`web-1-4-header-analysis`, `windows-2-1-smb-connection-test`,
`windows-2-2-smb-share-listing`, `windows-2-5-smb-null-session-connection`,
`windows-2-6-smb-null-session-share-enumeration`,
`windows-2-7-smb-user-enumeration-via-null-session`,
`windows-2-8-smb-comprehensive-null-session-enumeration`,
`windows-3-5-smb-full-credential-attack`,
`windows-8-1-single-service-credential-discovery`.

Each declares a single-file render contract. Two classes are deliberate
exceptions:

- `platform/backend/app/data/external-targets.yaml` records public OSINT
  markers that learners are meant to find on the open web;
- decoy flags are labelled as decoys and are not answers.

The tester manifests still carry expected values for the static labs. They are
generated and needed by the acceptance harness, so they are part of the
migration, not a hand edit.

## Why it matters

A static flag that is public is not a control. It weakens completion evidence and
any certificate that depends on it. It is also the cheapest issue to fix now and
the most awkward to explain after a learner has shared a link.

## Runtime verification

Static checks prove the contract is well formed, not that the container can write
the path. Before a batch merges, build the image and run the same wrapper:

```bash
bash scripts/verify-flag-render.sh <lab-slug> [<lab-slug> ...]
```

Run it on a host with Docker and the repository checked out at the branch. It
builds each target, writes a test flag through the launcher override, and checks
the file. The launcher creates the parent directory, so a contract can target a
path the image only creates at runtime. The first runtime pass found
`malware-1-1` writing to `/tmp/samples`, which the image does not keep; the
launcher now creates it. The replace-mode batch was verified the same way: the
report, history, and log content survives and the value rotates. Batch 4 was
sampled the same way: a PHP page and `smb.conf` keep their content while the flag
rotates.

## Plan

1. **Keep the gate.** `--fail-on-leaks` runs in the Quality workflow on every
   push.
2. **Rotate the static labs in batches.** Environment-driven labs first: add a
   `FLAG` value that matches the graded flag so the launcher can rotate it. Baked
   labs next: add the render contract and let the wrapper write `LAB_FLAG`.
3. **Keep manifests free of live values.** Generate them from the private
   overlay, or compare against the hash instead of a literal.
4. **Assume past public flags are compromised.** Rotate them at the next
   deployment rather than keeping a value that has been readable on GitHub.
5. **Tighten the gate.** Once the migration is complete, add
   `--fail-on-static` so a new static lab cannot land.

## Limits

The audit is a heuristic. It catches literal `OCR{...}` values; it does not prove
that a flag cannot be derived from a lab image. Review every flagged value by
hand, and treat the private host and the deployment secrets as part of the
boundary.
