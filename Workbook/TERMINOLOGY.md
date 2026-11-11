# Cross-Curriculum Terminology

Generated from `curriculum-glossary.yaml`. Do not edit this page by hand.
These definitions take precedence in learner-facing prose, workbook
evidence notes, analytics, assessment reports, and PDF output.

## Core terms

| Term | Definition |
|---|---|
| **Exercise** | A single task inside a lab or workbook. An exercise has instructions and, when the platform requires it, one flag. |
| **Lab** | A self-contained practice environment with one or more targets, services, and exercises. A lab is launched from the exercise panel. |
| **Chapter** | A curated group of exercises and labs around one topic. A chapter has a stable display identifier such as WIN01 or NET02. |
| **Track** | A themed pathway made of chapters, levels, exercises, and labs, such as Windows Penetration Testing or OSINT. |
| **RangeBox** | The browser-delivered Linux practice desktop provided by the platform. It is the workstation where terminal and browser activities run. |
| **Target** | The specific host, service, or asset assigned to an exercise. Only the target shown in that exercise is authorized. |
| **Host** | A device, container, or virtual machine on a network with an address. |
| **Service** | A program that provides a function, often by listening on a port. A service is not automatically a vulnerability. |
| **Asset** | A host, service, data set, identity, or process with value in a scenario. An asset is what the activity is trying to protect or understand. |
| **Evidence** | An artifact or record that supports a statement, such as command output, a log line, a packet capture, or a screenshot. Collect the minimum needed and handle it safely. |
| **Observation** | A statement directly present in output or evidence, without interpretation. |
| **Interpretation** | A reasonable meaning assigned to evidence. An interpretation requires verification before it becomes a finding. |
| **Hypothesis** | A testable explanation for an observation. It can be confirmed or refuted by an approved check. |
| **Finding** | A conclusion supported by evidence, with a stated confidence and, where relevant, an impact. A finding is stronger than an interpretation and weaker than a validated impact. |
| **Vulnerability** | A weakness that could be used by a threat actor to affect a system or its data. A version match or an open port alone does not establish a vulnerability. |
| **Exposure** | A condition where an asset, service, or data set is accessible beyond its intended scope. Exposure may be caused by a vulnerability or a misconfiguration, but the terms are not interchangeable. |
| **Misconfiguration** | A setting that differs from the intended or secure baseline. A misconfiguration may create exposure but is not automatically a vulnerability. |
| **Exploit** | An action, tool, or technique that uses a weakness to affect a target. Exploitation is allowed only inside an explicitly authorized lab. |
| **Impact** | A demonstrated effect on confidentiality, integrity, availability, identity, or process state. |
| **Confidence** | How strongly the evidence supports a conclusion, expressed as low, medium, or high with a reason. |
| **Remediation** | A change that addresses the root cause and reduces risk. Remediation is not the same as hiding the symptom. |
| **Rollback** | Reversing a change to restore the previous state. A rollback is used when a change is unsafe, ineffective, or no longer needed. |
| **Cleanup** | Removing disposable files, credentials, sessions, and other artifacts after an activity so the next learner starts clean. |
| **Flag** | A training completion token in OCR{...} format. A flag confirms completion; it is not an IOC, a vulnerability, or proof of impact. |

## Evidence ladder

Use these words in this order. Do not skip from an observation to a
finding, impact, or remediation claim.

| Level | Term | Definition |
|---:|---|---|
| 1 | **Observed** | Directly present in output or evidence. |
| 2 | **Inferred** | A reasonable interpretation that still requires more verification. |
| 3 | **Validated** | Confirmed through an approved controlled test. |
| 4 | **Impacted** | A demonstrated effect on confidentiality, integrity, availability, identity, or process state. |
| 5 | **Remediated** | The root cause has been changed. |
| 6 | **Verified** | A regression test confirms the correction. |

## How to use the ladder

- **Observed:** quote or show the output.
- **Inferred:** say what you think it means and what would verify it.
- **Validated:** name the approved test and its result.
- **Impacted:** name the affected confidentiality, integrity, availability,
  identity, or process state.
- **Remediated:** name the root-cause change.
- **Verified:** name the regression test that confirms the correction.

A flag confirms completion. It is not a finding or proof of impact.
