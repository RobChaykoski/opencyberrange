# SWSEC01: Software Security Foundations

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `SWSEC01` — Software Security Foundations
    **Prerequisites:** `WEB02` — SQL Injection and Web Exploitation
    **Recommended next:** `MAL01` — Malware Fundamentals
<!-- END GENERATED CHAPTER POSITION -->

## What this course is

Software security is the practice of reading, testing, and fixing software so
that it does what its users expect and nothing more. This course starts with
reading code and noticing missing checks, then moves into injection bugs,
access-control mistakes, and eventually writing an exploit against a safe,
local target.

You do **not** need to be an experienced programmer to start. If you can read a
short page, follow a link, and explain what you observed, you can begin.

## The five-level path

| Level | Theme | What you will do |
|---|---|---|
| 1 | Reading Code for Bugs | Inspect shipped JavaScript and find a hidden route |
| 2 | Injection and Exploitation | Turn untrusted input into an extra command |
| 3 | Authentication and Authorization | Find broken access-control checks |
| 4 | Memory Safety and Exploit Development | Triage a crash and write a first exploit script |
| 5 | Capstone Exploit Development | Build and document an end-to-end exploit |

Levels 1 and 2 are browser-only and are the DevFest starter pair. Levels 4 and
5 will use a RangeBox or terminal; they are not required for the DevFest
competition.

## Safety and ethics

- Every target in this course is fictional. There is no real attendee, speaker,
  customer, or production system in the lab.
- The lab containers are isolated. You cannot reach the public internet from a
  target, and the platform drops container capabilities.
- The command-injection exercise deliberately runs a shell inside its own
  container. That is the bug you are learning to find, not permission to attack
  anything outside the lab.
- Never test a system you do not own or have written permission to test.
- If you find a real secret outside the lab, stop and tell a facilitator.

## How to work

1. **Read** the scenario and objectives.
2. **Observe** the page, the source, or the response.
3. **Try** one small change at a time.
4. **Record** what you sent and what came back.
5. **Explain** the bug and the fix in your own words.

Using hints is allowed. The first hint is a starting point, not a penalty.

## Start here

- [Hidden Export Route](01_Hidden_Export_Route.md)
- [Diagnostics Command Injection](02_Diagnostics_Command_Injection.md)
- [Chapter Review](03_Chapter_Review.md)
