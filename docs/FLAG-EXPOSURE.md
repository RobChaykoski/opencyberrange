# Flag exposure

Status: **audit and answer-leak gate in place; static-flag migration not
started.**

Flags are the graded answers for a lab. The platform must know them, but a
learner must not be able to read them from the public repository before class.
This page records the current exposure and the plan to close it.

## How flags work today

- **222 labs.** **116** labs rotate per session: 75 environment-driven labs match a
  `FLAG` / `*_FLAG` compose value to the graded hash, and 41 baked labs declare a
  render contract. **106** labs keep a static value. Their flag is written in
  `lab.yaml`, and often again in the compose environment or the lab source. That
  value is public.
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

Current result: **106 static labs**, **0 leaked answers** outside the lab tree.
The Workbook capstone page that printed a real marker was replaced with a
read-the-route instruction. The first rotation batch is:

- `linux-1-6-version-vulnerability-identification`;
- `web-1-2-technology-identification`;
- `web-1-6-comprehensive-web-reconnaissance`;
- `windows-2-3-smb-anonymous-share-access`;
- `malware-1-1-eicar-triage`.

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

## Plan

1. **Keep the gate.** `--fail-on-leaks` runs on every docs or lab change.
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
