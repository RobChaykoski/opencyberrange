# Evidence Notes and Technical Communication

This activity teaches you to record reproducible steps and explain a finding
clearly. Good notes help you troubleshoot, learn from mistakes, and communicate
without exposing sensitive data.

You will not run a new network command. Use the output you already collected in
the network, enumeration, and log activities.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, for notes and optional screenshots. |
| **Notes file** | Your own notes, outside RangeBox. | **Yes. This is the main workspace.** |
| **RangeBox terminal** | The text window inside RangeBox. | Only to review output you already produced. |
| **Assigned target** | A practice server named in the earlier labs. | **No new target is contacted.** |

This activity has **no new target** and **no new flag**. Use only the evidence
from your own earlier activities. Do not collect real personal data.

### What you need

- [ ] Your notes from the network, enumeration, and log activities.
- [ ] Optional: one screenshot from your own lab screen.
- [ ] About **20–30 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- define observation, evidence, interpretation, confidence, screenshot, command
  output, and redaction;
- write a reproducible evidence note;
- separate observation from interpretation;
- choose a confidence level and explain it;
- take or describe a screenshot that shows only necessary context;
- compare a weak finding statement with a strong one;
- redact credentials and personal information.

## Words to Know

| Term | What it means |
|---|---|
| **Observation** | What you directly saw, such as a line of output. |
| **Evidence** | Information that supports a statement, such as command output, a log line, or a screenshot. |
| **Interpretation** | What you think the evidence means. |
| **Confidence** | How strongly the evidence supports the interpretation: low, medium, or high. |
| **Screenshot** | An image of a screen or window. It can expose more than you intend. |
| **Command output** | Text a command printed. Copy text when you can; use a screenshot only when necessary. |
| **Redaction** | Hiding or removing sensitive details from a note, image, or description. |

## The Evidence Note Template

Copy this template into your notes for each finding.

```text
Timestamp:
Target:
Action:
Result:
Meaning:
Next step:
Confidence:
Redactions:
```

| Field | What to write |
|---|---|
| **Timestamp** | When you did the action, including the time zone if known. |
| **Target** | The hostname and port, or "local RangeBox" for a local action. |
| **Action** | The exact command or step, with replaceable values filled in. |
| **Result** | The relevant output, copied as text when possible. |
| **Meaning** | What the result shows, in one or two sentences. |
| **Next step** | The next safe action, or "ask teacher" if uncertain. |
| **Confidence** | Low, medium, or high, with a reason. |
| **Redactions** | What you removed or hid, and why. |

### Example

```text
Timestamp: 2026-11-11 10:20 UTC
Target: network.lab:8080
Action: curl -I http://network.lab:8080/status.json
Result: HTTP/1.1 200 OK; Content-Type: application/json
Meaning: The target accepted the connection and returned a successful response.
Next step: Record the status and submit the lab flag if not already submitted.
Confidence: High for "the service answered"; not enough to claim a vulnerability.
Redactions: None; no credentials or personal data were present.
```

## Observation, Interpretation, and Confidence

| Statement | Observation or interpretation? | Why |
|---|---|---|
| The output says `HTTP/1.1 200 OK`. | Observation | It is directly in the output. |
| The web service is working. | Interpretation | It is a conclusion from the status. |
| Port 8080 is open. | Observation from the scan | The scan reported it. |
| The service is vulnerable. | Unsupported interpretation | A port and service label do not prove a weakness. |
| One source made three failed requests. | Observation | The log shows the requests. |
| The source was attacking the site. | Interpretation with low confidence | The log alone does not prove intent. |

**Confidence** is not a feeling. Give a reason:

- **High:** direct output from the assigned target, repeated, and consistent.
- **Medium:** one clear observation, but missing context.
- **Low:** a clue, a guess, or evidence that could have another explanation.

## Reproducible Steps

A step is reproducible when another student can follow it and see the same kind
of result.

Include:

1. the target;
2. the exact command or action;
3. the order of steps;
4. the relevant output;
5. what you expected;
6. what you actually saw.

Do not include:

- passwords or tokens;
- real personal information;
- unrelated windows;
- commands you did not run;
- results you copied from someone else.

## Screenshots and Redaction

Use a screenshot only when the visual context matters. Prefer copied text when
the text is enough.

### Before you take a screenshot

- [ ] Show only the window needed for the evidence.
- [ ] Close unrelated tabs and messages.
- [ ] Hide or crop password fields, tokens, email addresses, names, and personal
      information.
- [ ] Do not capture another student's screen or account.
- [ ] Check the image before you save or share it.

### After you take a screenshot

- [ ] Redact anything sensitive.
- [ ] Store it with your notes, not in a group chat.
- [ ] Share it only with your teacher through the approved channel.
- [ ] If it contains a real credential, tell your teacher and follow their
      instructions.

**This workbook uses text descriptions instead of screenshots.** If your teacher
provides screenshots, read their alt text and follow the same redaction rules.

## Weak and Strong Findings

| Weak finding | Why it is weak | Stronger finding |
|---|---|---|
| "The server is hacked because port 8080 is open." | An open port is not a compromise. | "Port 8080 accepted a connection and identified itself as HTTP. This shows a web service is running. It does not show a vulnerability." |
| "The log proves an attack." | One log excerpt lacks context. | "One source made three 404 requests followed by one 200. This is consistent with probing, but it could also be a broken link. Confidence: low without more context." |
| "The password is `...`." | It exposes a credential. | "A credential appeared in the output. I redacted it and told my teacher." |
| "I think it is bad." | It has no evidence or meaning. | "The response was `403 Forbidden`. The service refused the request. I do not know why." |

A strong finding is specific, evidence-based, and honest about uncertainty.

## If You Get Stuck

| Problem | What to do |
|---|---|
| You did not save the output | Re-run the step only if it is safe and still authorized. Otherwise write "output not saved" and ask. |
| You cannot explain the result | Write the observation, mark confidence low, and ask. |
| A screenshot contains a password | Do not share it. Tell your teacher, redact it, or delete that copy only if your teacher agrees. |
| You copied a command from someone else | Do not claim it as your own. Run it yourself only if it is in the activity, or ask. |
| Your note has no target | Add the target from the exercise panel. If you do not know it, stop and ask. |
| Your finding sounds like a guess | Separate observation from interpretation and lower the confidence. |

## Record Your Evidence

Write one full evidence note from an earlier activity. Then answer:

1. What is the difference between observation and interpretation?
2. What makes a step reproducible?
3. Why is copied text usually better than a screenshot?
4. What should you redact from a screenshot?
5. What does high confidence require?
6. Why is "the server is hacked" a weak finding?
7. What should you do if a screenshot contains a real credential?
8. Why does a flag not prove a vulnerability?

## What Success Looks Like

You are ready to continue when you can show:

- one completed evidence note with all template fields;
- one observation and one interpretation clearly separated;
- one confidence level with a reason;
- one redaction decision;
- one weak statement rewritten as a strong statement;
- a clear statement that you did not collect real personal data.

This activity has **no new flag**. Your evidence is your note and your
explanation.

## Key Takeaways

- Evidence supports a statement; interpretation explains what you think it means.
- A reproducible step includes target, action, order, result, expectation, and
  actual result.
- Confidence needs a reason.
- Prefer copied text over screenshots.
- Redact credentials, personal information, and unrelated context.
- A strong finding is specific, evidence-based, and honest about uncertainty.
- A flag confirms completion, not a vulnerability.

Next: [Guided Cybersecurity Challenge](09_Guided_Cybersecurity_Challenge.md).
