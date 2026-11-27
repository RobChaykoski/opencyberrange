# Alternate-path review plans

A lab proves an intended path. This folder records the bypass checks that prove
an alternate path does not skip the learning objective.

Create `<lab-slug>.yaml`:

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

Rules:

- `lab_id` is the directory slug.
- `intended_path` names the concept the lab teaches.
- Each bypass check has a name, a command, a `must_not_contain` marker, and a
  rationale.
- The command runs in the lab network as the learner; it must not use the flag
  value or an instructor secret.
- A check passes when the output does **not** contain the flag.
- Run the check live and record the date and result in the release evidence.
- A lab with no plan is reported as `info` until the coverage gate is enabled.

`python scripts/lab_qa.py --static` validates the shape and reports coverage.
The live bypass runner is a follow-up; see
[LAB-QA-PIPELINE.md](../../../docs/LAB-QA-PIPELINE.md#5-path-and-bypass-validation).
