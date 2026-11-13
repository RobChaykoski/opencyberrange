# Topology Forensics: Choose Your Pace

Two exercises share the same evidence question: **which path did the request take
through the router?** Choose the format that fits how you want to learn today.

| Exercise | Format | Time | Support |
|---|---|---|---|
| 2.2 Guided Path Reconstruction | Step-by-step | ~25 min | Every command and checkpoint is given |
| 2.3 Independent Path Reconstruction | Independent | ~35 min | Objectives and a recording template; you choose the method |

Both exercises use the same node status endpoint, SSH access, and routed-path
evidence. The independent variant adds a decoy service so you must verify the
service identity before using it as evidence.

## What you will practise

- reading a topology from a status document;
- distinguishing a management address from a link address;
- following a host default route through a router;
- confirming IPv4 forwarding;
- writing a short path record that another analyst can reproduce.

## Rules

- Use only the management addresses shown in the exercise.
- Do not change routing or forwarding configuration.
- The case token is on the protected service, not the decoy.
- Record the path; do not record the token in a shared document.
