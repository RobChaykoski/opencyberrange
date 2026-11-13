# Detection and Triage: YARA and Evidence

Two exercises build a detection workflow:

| Exercise | Focus | Time |
|---|---|---|
| 2.2 YARA Fundamentals | Write a string rule, scan samples, find the match | 30 min |
| 2.3 YARA Incident Triage | Match the artifact, then correlate the incident log | 40 min |

The first exercise teaches the rule. The second pairs the rule with the existing
log-analysis and incident-response skill: a match is a lead, and the log entry is
the context that turns it into a finding.

## What you will practise

- writing a YARA rule with a string and a condition;
- scanning a directory and reading the match output;
- identifying a control file that should not match;
- correlating a file marker with a process/quarantine log;
- writing a short evidence note.

## Rules

- These are static, benign text samples. Nothing executes.
- Do not treat a YARA match as proof of compromise.
- The case token is in the evidence, not in the rule.
