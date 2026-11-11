# AI01: AI Security Foundations

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `AI01` — AI Security Foundations
    **Prerequisites:** `WEB02` — SQL Injection and Web Exploitation
    **Recommended next:** `WIN01` — Enumeration
<!-- END GENERATED CHAPTER POSITION -->

!!! note "AI-assisted content"
    This chapter and its lab walkthroughs were drafted with AI assistance and
    reviewed by a human maintainer. Verify every command and flag against the
    running lab. See `BUILD_NOTICE.md` in the repository root for attribution
    and the full AI-assistance disclosure.

## Why AI Systems Need Their Own Security Model

Large language models do not execute code the way a web server does. They read
text, predict a response, and sometimes call tools. The security boundary is
not a parser or a memory allocator; it is the instruction hierarchy the
application asks the model to follow. When user text, retrieved documents, and
system instructions all arrive as natural language, an attacker can try to
change which instruction the model treats as authoritative.

This chapter starts with three beginner exercises that demonstrate the core
failure modes without requiring a GPU or an external API. Each lab runs a small
deterministic assistant inside the lab network. The assistant is intentionally
vulnerable in one specific way, so you can focus on the attack pattern rather
than on model behaviour that changes between versions.

## The AI Hacking Stream

The stream starts with foundations and moves toward agentic systems:

| Level | Focus | Status |
|-------|-------|--------|
| 1 | AI security foundations: prompt injection and jailbreaks | Available |
| 2 | Prompt injection at scale and instruction hierarchy | Planned |
| 3 | LLM data exposure, RAG, and secret handling | Planned |
| 4 | AI agents, tool use, and action abuse | Planned |
| 5 | Model supply chain and adversarial ML | Planned |
| 6 | AI-assisted security operations and capstone | Planned |

## What You Will Learn

- **Prompt injection**: override the instructions an assistant was given
- **Policy bypass**: move past a keyword filter with role-play and authority
  framing
- **Indirect injection**: plant instructions in a document the assistant reads
- **Defence**: why secrets must stay outside the model context and why output
  must be treated as untrusted

## Connection Details

| Exercise | Target | Service |
|----------|--------|---------|
| 1.1 | `assistant.lab` | HTTP 8080 |
| 1.2 | `safechat.lab` | HTTP 8080 |
| 1.3 | `tickets.lab` | HTTP 8080 |

Open the target in the lab browser, or use `curl` from a terminal. Add the
hostname shown in the exercise panel to `/etc/hosts` if your environment does
not resolve `.lab` names automatically.

## A Note on the Targets

These labs do not call a real language model. Each container runs a small
rule-based Python service that implements the vulnerable behaviour for the
exercise. That keeps the labs deterministic, fast, and safe to run offline. The
attack patterns are the same ones you will test against real LLM applications.

!!! warning "Authorised training only"
    Prompt injection and jailbreak testing against systems you do not own or
    have written permission to assess is not acceptable. Everything in this
    chapter runs against the isolated lab target.
