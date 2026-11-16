# AI security and agentic skill labs

These labs follow the OWASP Agentic Skills Top 10 (AST10). The
machine-readable plan is in
`platform/backend/app/data/owasp-security-baseline.yaml`; the validation matrix
is in [`OWASP-SECURITY-BASELINE.md`](OWASP-SECURITY-BASELINE.md).

The existing AI labs (`ai-1-1-prompt-injection-basics`,
`ai-1-2-jailbreak-policy-bypass`, `ai-1-3-indirect-prompt-injection`) remain
the introductory sequence. The labs below add skill governance, manifest
review, isolation, provenance, and update control.

The platform does not install or execute a third-party agent skill. Every
manifest and upstream page is fictional and local.

## Sequence

| Lab | Risk | Title | Target | Level | Minutes |
|---|---|---|---|---|---|
| AI-LAB-01 | AST01 | Inspect a malicious skill manifest | Local manifest | beginner | 60 |
| AI-LAB-02 | AST02 | Skill provenance and registry trust | Platform | intermediate | 60 |
| AI-LAB-03 | AST03 | Reduce an over-privileged skill | Local manifest | intermediate | 60 |
| AI-LAB-04 | AST04 | Insecure metadata and hidden keys | Local manifest | intermediate | 60 |
| AI-LAB-05 | AST05 | Pin untrusted external instructions | Local copy | intermediate | 60 |
| AI-LAB-06 | AST06 | Isolate an agent workflow | Platform | intermediate | 75 |
| AI-LAB-07 | AST07 | Detect update drift | Platform | beginner | 45 |
| AI-LAB-08 | AST08 | Scanner bypass and behavioural review | Local copy | advanced | 75 |
| AI-LAB-09 | AST09 | Skill inventory and approval | Platform | beginner | 45 |
| AI-LAB-10 | AST10 | Cross-platform manifest mapping | Local manifest | intermediate | 60 |

## Evidence

Every lab requires:

- the manifest, request, or diff that supports the finding;
- the decision: allow, block, or require review;
- the reason, with the specific field or instruction that caused it;
- the control that prevents recurrence;
- a verification step or regression check.

A model response alone is not evidence. Quote the instruction, field, or diff.

## Lab notes

### AST01 — malicious skill

Read a fictional `SKILL.md`, `skill.json`, or `manifest.json` without executing
it. Identify hidden instructions, unexpected commands, and data paths. Write a
block or approve decision with a reason.

### AST02 — provenance

Compare a signed and an unsigned skill package. Trace the publisher, version,
hash, and review record. Reject the package that fails the provenance chain.

### AST03 — least privilege

List the permissions a skill requests. Remove every permission the workflow
does not need. Show that the workflow still succeeds with the reduced scope.

### AST04 — metadata

Parse a manifest with duplicate, hidden, or nested keys. Show how a naive parser
and a safe parser disagree. Write the schema and rejection rule.

### AST05 — external instructions

Compare a pinned instruction page with a changed copy. Identify an instruction
that changes the agent's goal. Add a hash and review gate before use.

### AST06 — isolation

Draw the agent, tool, and data boundaries. Confirm no egress, no host mount, and
no shared secret. Test teardown and state reset.

### AST07 — update drift

Pin a manifest by version and digest. Replace one byte in a local copy. Show the
verification failure and the safe fallback.

### AST08 — scanning

Bypass a naive keyword scanner with a benign paraphrase. Explain why the
scanner missed the behaviour. Write a behavioural check and a human review
step. Do not use a real malicious payload.

### AST09 — governance

Build an inventory of fictional skills and owners. Add an approval, review
date, and revocation path. Record the audit event for one decision.

### AST10 — cross-platform

Map two fictional platform manifests to one reviewed schema. Identify fields
that change meaning across platforms. Write a portability warning and a safe
import rule.

## Safety

- Use fictional manifests, pages, and accounts only.
- Do not install, execute, or fetch a real third-party skill.
- No internet egress from a learner lab.
- No real credentials, personal data, or proprietary prompts.
- Treat model output as untrusted text; never let it trigger a tool directly.
- Keep the lab inside the default-deny network and disposable storage.

## References

- [OWASP Agentic Skills Top 10](https://owasp.github.io/www-project-agentic-skills-top-10/)
- [OWASP Secure Coding with AI Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
- [OpenCRE Explorer](https://www.opencre.org/explorer)

## Attribution

OWASP Agentic Skills Top 10 is CC BY-SA 4.0, OWASP Agentic Skills Top 10
project team. OWASP Cheat Sheet Series is CC BY-SA 4.0, OWASP Cheat Sheet
Series Team. The Threat Modeling Manifesto is CC BY 4.0, the Threat Modeling
Manifesto working group. OpenCRE is CC0-1.0, OWASP OpenCRE project. See
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
