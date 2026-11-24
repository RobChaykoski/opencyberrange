# OSINT03: Canary Tokens and Deception

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `OSINT03` — Canary Tokens and Deception
    **Prerequisites:** `OSINT02` — Mobile OSINT
    **Recommended next:** `IAM01` — Identity and Access Foundations
<!-- END GENERATED CHAPTER POSITION -->

This chapter adds a defensive tripwire to the OSINT pathway. You will use a
lab-owned canary token, read its alert console, and separate a human visit from
automated noise.

A canary token is not a tracking device for a person. It is a tripwire for a
unique URL, file, or credential. The alert tells you that something was
accessed. It does not tell you who accessed it or why.

## What you will practise

- reading a public page for instrumentation before clicking;
- triggering a canary token in an isolated lab;
- comparing user agents, referers, and fetch metadata;
- writing a finding that separates observation, inference, and unknown.

## Chapter map

| Exercise | Focus |
|---|---|
| 3.1 | Noise in the Nest: triage a canary alert among bot, scanner, and monitor traffic |

## Safety

The portal, documents, and console are synthetic. They contain no real person,
customer, staff member, or credential. The canary console runs inside the lab
network and does not send data to a third party.
