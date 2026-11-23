# AI01: AI Security Foundations

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `AI01` — AI Security Foundations
    **Prerequisites:** `WEB02` — SQL Injection and Web Exploitation
    **Recommended next:** `AI02` — Agentic AI Security
<!-- END GENERATED CHAPTER POSITION -->

!!! note "AI-assisted content"
    This chapter and its lab walkthroughs were drafted with AI assistance and
    reviewed by a human maintainer. Verify every command and flag against the
    running lab. See `BUILD_NOTICE.md` in the repository root for attribution
    and the full AI-assistance disclosure.

!!! note "The Trailline universe"
    These exercises take place at [Trailline Security & GRC](../TRAILLINE-UNIVERSE.md),
    a fictional consultancy. TrailGuard AI, Elena Vance, Marcus Chen, Priya
    Patel, and the `svc-trailguard-bot` service identity recur across the AI,
    identity, and GRC labs. All names and data are synthetic.

## Why AI Systems Need Their Own Security Model

Large language models do not execute code the way a web server does. They read
text, predict a response, and sometimes call tools. The security boundary is
not a parser or a memory allocator; it is the instruction hierarchy the
application asks the model to follow. When user text, retrieved documents, and
system instructions all arrive as natural language, an attacker can try to
change which instruction the model treats as authoritative.

This chapter starts with three beginner exercises that demonstrate the core
failure modes without requiring a GPU or an external API. Each lab runs a small
deterministic assistant inside the lab network. TrailGuard AI is intentionally
vulnerable in one specific way per exercise, so you can focus on the attack
pattern rather than on model behaviour that changes between versions.

## The AI Hacking Stream

The stream starts with foundations and moves toward agentic systems:

| Level | Focus | Status |
|-------|-------|--------|
| 1 | AI security foundations: prompt injection, jailbreaks, and indirect injection | Available |
| 2 | Agentic AI, RAG, and tool use | Available (`AI02`) |
| 3 | LLM data exposure, RAG poisoning, and secret handling | Planned |
| 4 | Multi-agent systems and autonomous exploitation | Planned |
| 5 | Model supply chain and adversarial ML | Planned |
| 6 | AI-assisted security operations and capstone | Planned |

## What You Will Learn

- **Prompt injection**: override the instructions an assistant was given
- **Policy bypass**: move past a keyword filter with role-play and authority
  framing
- **Indirect injection**: plant instructions in a document the assistant reads
- **Defence**: why secrets must stay outside the model context, why retrieved
  content is data, and why output must be treated as untrusted

## Connection Details

| Exercise | Target | Service |
|----------|--------|---------|
| 1.1 | `assistant.lab` | HTTP 8080 |
| 1.2 | `safechat.lab` | HTTP 8080 |
| 1.3 | `tickets.lab` | HTTP 8080 |

The hostnames are per-lab aliases for the same deterministic mock. The story
continues in `AI02`, where TrailGuard gains tools and the impact moves from a
leaked sentence to an unauthorised export.
