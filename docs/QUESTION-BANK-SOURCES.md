# Certification question-bank sources and career mapping

Status: **admin-curated.** The shared bank is
`platform/backend/app/data/certification-question-banks.yaml`.

## Policy

- Every item is written for OpenCyberRange. The project does not copy exam
  questions, braindumps, NDA material, or a third-party quiz dump.
- Public standards, government guidance, vendor objective pages, and OER
  references are used to check the facts and provide an authoritative link.
- "Free and open" here means the reference is publicly readable and reusable
  for fact-checking. The question text and explanations remain original.
- Each item names the certification domain, the objective it tests, a public
  reference, and a career pathway.
- The bank is practice, not a certification exam and not a predictor of exam
  or job performance.

## Current coverage

The shared bank carries **81 original items across 9 pathways** (reviewed
2026-11-12):

| Pathway | Code | Items | Tracks | Career pathways |
|---|---|---:|---|---|
| CompTIA Security+ | SY0-701 | 9 | network, linux, windows, web, osint, forensics, identity, high-school | SOC analyst, security administrator, junior penetration tester, IT auditor |
| CompTIA CySA+ | CS0-004 | 9 | forensics, malware, osint, windows, network, ot | SOC analyst, threat hunter, incident responder, vulnerability analyst |
| CompTIA PenTest+ | PT0-003 | 9 | web, software-security, linux, windows, network | Penetration tester, red team operator, security consultant, application security tester |
| CompTIA Network+ | N10-009 | 9 | network | Network administrator, network engineer, NOC analyst, network security analyst |
| CompTIA Linux+ | XK0-006 | 8 | linux | Linux systems administrator, systems engineer, cloud operations engineer, site reliability engineer |
| Microsoft SC-900 | SC-900 | 8 | identity, windows | Identity and access administrator, security operations analyst, compliance analyst, Microsoft 365 administrator |
| ISC2 Certified in Cybersecurity | CC | 9 | high-school, network, linux | Security analyst, access control administrator, junior SOC analyst, IT support technician |
| OWASP Top 10 | 2021 | 10 | web, software-security | Application security engineer, web developer, penetration tester, security code reviewer |
| OWASP Top 10 for LLM Applications | 2025 | 10 | ai | AI security engineer, ML engineer, AI governance analyst, application security engineer |

The lab-specific `quiz.yaml` banks remain the first choice for an exercise.
The shared bank is the fallback and the source for weekly challenge boards.

## Open/public references used

| Source | Use | Licence / terms |
|---|---|---|
| [NIST CSRC](https://csrc.nist.gov/) | SP 800-53, 800-61, 800-63B, 800-82, 800-86, 800-115, 800-137, 800-207, 800-41, 800-52; FIPS 180-4 | U.S. Government work; public domain |
| [CISA](https://www.cisa.gov/) | Phishing guidance; Known Exploited Vulnerabilities | U.S. Government work; public domain |
| [OWASP](https://owasp.org/) | Top 10, ASVS, logging, password storage, MFA, WSTG | CC BY-SA 4.0 unless otherwise stated |
| [OWASP GenAI Security Project](https://genai.owasp.org/) | LLM Top 10 2025 | CC BY-SA 4.0 unless otherwise stated |
| [MITRE ATT&CK](https://attack.mitre.org/) | Credential Access and post-exploitation tactics | MITRE ATT&CK terms of use |
| [Microsoft Learn](https://learn.microsoft.com/) | SC-900, Entra, Defender, Purview | CC BY 4.0 |
| [IETF RFC Editor](https://www.rfc-editor.org/) | RFC 1918, RFC 3596 | IETF Trust legal provisions |
| [CompTIA certification pages](https://www.comptia.org/en-us/certifications/) | Current exam codes, domains, weights, and career roles | Objectives used as reference; questions are original |

When a source's licence requires attribution, keep the reference label and URL
on the item and in this table. Do not paste a source's question text.

## Adding an item

1. Pick the pathway and the current domain from the pathway's official
   objectives page.
2. Write a scenario with one defensible answer and three plausible
   distractors.
3. Explain why the correct answer is right and why the distractors are wrong.
4. Add a public reference that a learner can open without an account.
5. Add a `career` value from the pathway's career list.
6. Run:

```bash
cd platform/backend
python -c "from app.services import certification_quiz as c; print(c.validate_banks())"
python -m pytest tests/test_certification_quiz.py -q
```

The validator rejects duplicate ids, missing objectives, missing careers,
invalid answer indexes, short explanations, non-HTTPS links, and self-references.
