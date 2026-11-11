# NET03: Firewalls and Network Policy

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `NET03` — Firewalls and Network Policy
    **Prerequisites:** `NET02` — PCAP Forensics
    **Recommended next:** `WEB01` — Web Reconnaissance
<!-- END GENERATED CHAPTER POSITION -->

## Welcome

This chapter moves from observing network traffic to understanding the policy
that decides whether traffic is allowed. You will read firewall rules, compare
them with expected traffic, and explain the difference between a blocked
connection and a missing service.

## Before You Begin

- [ ] Completed **NET02: PCAP Forensics**, or can explain how to read a packet capture.
- [ ] Can use the RangeBox terminal and a text editor.
- [ ] Have your notes file ready.

## What You Will Learn

By the end of this chapter, you will be able to:

- explain the purpose of a firewall and a network policy;
- read a simple rule set from top to bottom;
- distinguish default deny, explicit allow, and implicit deny;
- explain why a filtered port is not proof of a vulnerability;
- compare a rule set with observed traffic;
- recommend a safe policy change and a rollback step.

## Activities

1. [Firewall Fundamentals](01_Firewall_Fundamentals.md) — read a rule set and
   predict which traffic is allowed.
2. [Firewall Policy Hardening](02_Firewall_Policy_Hardening.md) — tighten a
   policy, verify the result, and record a rollback.

## Scope and Safety

Use only the firewall target and rule files provided in the exercise. Do not
change firewall settings on your student device, school network, or any system
outside the lab. A policy change in a lab must include a rollback step.

## Evidence

For each activity, record the rule, the observed traffic, the expected result,
the actual result, and your confidence. A blocked packet is an observation, not
proof that a service is vulnerable.
