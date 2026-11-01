---
name: OpenCyberRange Software Security
description: Use when writing, reviewing, or teaching OpenCyberRange software-security and Web-track content for non-programmers. Explains programming concepts in plain language, focuses on bad programming practices and the exploit endgame, and deliberately de-emphasises object-oriented programming and architecture except where they clarify a trust boundary or a bug.
---

# OpenCyberRange Software Security

Use this skill for the **Software Security** track and the **Web Application
Security** track when the learner may not be a programmer. It is a teaching and
authoring skill, not a general programming course.

Companion skills:

- `opencyberrange-design/references/course-content.md` — lab contract, workbook
  structure, and safe content rules.
- `opencyberrange-inclusive-curriculum` — who the learner is and how to write a
  scenario without stereotypes.

## The core stance

There are two different kinds of programming knowledge:

| Builder knowledge | Breaker knowledge |
|---|---|
| How to design classes and objects | Where untrusted input enters |
| How to structure an application | Where that input is trusted |
| Design patterns, frameworks, layers | Which check is missing |
| Maintainability and architecture | What the attacker can control or reach |
| "How do I add a feature?" | "How do I make this do something it was not meant to do?" |

Object-oriented programming, design patterns, and architecture are valuable for
people who build and maintain software. They are **not** the first thing a
non-programmer needs in order to reason about an exploit.

From the exploit endgame, the most important thing to understand is **bad
programming practices**: the small, ordinary shortcuts that turn user input,
files, sessions, or memory into attacker-controlled behaviour.

Teach the builder view only when it explains a trust boundary or a bug. Do not
make a learner sit through inheritance, MVC layering, microservices, or design
patterns before they can spot a missing authorization check.

## The exploit endgame

Every software-security lab should be explainable as five questions:

1. **What does the attacker control?** A form field, URL parameter, header,
   cookie, filename, uploaded file, API body, environment value, or memory
   contents.
2. **Where does it go?** A database query, shell command, file path, HTML page,
   template, deserializer, memory buffer, authorization decision, or log.
3. **What check is missing or wrong?** Validation, encoding, parameterization,
   bounds checking, authentication, authorization, allowlisting, or rate
   limiting.
4. **What is the impact?** Read data, change data, run a command, become another
   user, crash a process, or take over a host.
5. **How do you prove it?** A deterministic request, payload, crash, or flag
   that the learner can reproduce and explain.

If a lesson cannot answer those five questions, it is probably a programming
lesson, not a security lesson.

## Teaching non-programmers

### Start with behaviour, not syntax

1. **Show the app working.** What does the learner see and do?
2. **Show one input and one output.** No code yet.
3. **Show the smallest code path** between them (5–15 lines).
4. **Name the trust boundary.** "This value came from the browser."
5. **Point at the bad practice.** "The server put it straight into a shell."
6. **Ask what an attacker could change.** Then try it.
7. **Explain the fix in one sentence and one code change.**

Do not begin with a language tour, a framework diagram, or a class hierarchy.

### Use an analogy ladder

Every concept gets three layers:

1. **Everyday analogy** — a form at a front desk, a mailroom, a recipe, a
   bouncer, a numbered locker, a sentence where punctuation changes meaning.
2. **Technical term** — variable, parameter, validation, trust boundary, query,
   shell, buffer, pointer.
3. **Code line and consequence** — the exact line and what an attacker can do
   with it.

If the learner remembers only the analogy, they can still reason about the bug.

### Snippet rules

- 5–15 lines, one idea per snippet.
- Use realistic but fictional names; no real customer data.
- Show the input line, the dangerous line, and the output line.
- Prefer standard-library Python, JavaScript, SQL, or C over a framework.
- Avoid ORM magic, decorators, dependency injection, and metaprogramming in a
  first explanation.
- Highlight one line at a time in prose: "The problem is line 4."
- Show the safe version beside the unsafe version.

### Language rules

- Define every acronym and term on first use.
- Avoid "just", "simply", "obviously", and "everyone knows".
- Use second person and short sentences.
- Separate **what the code does** from **why it is dangerous**.
- Say "the server trusts this value" rather than "the input is unsanitised"
  before the learner knows what sanitisation means.
- Never shame a learner for missing a bug.

## Bad practices first

Build the course around a catalogue of ordinary bad practices, not a taxonomy of
programming languages.

High-value examples:

- trusting client-side input or client-side checks;
- building SQL with string concatenation;
- passing user input to a shell;
- joining a user-controlled path to a file root;
- checking authentication but not authorization;
- shipping secrets or admin routes in front-end code;
- deserialising untrusted data;
- using `eval` or dynamic code execution on input;
- missing bounds checks in C;
- integer overflow in size calculations;
- use-after-free or double-free;
- race conditions and time-of-check/time-of-use;
- permissive CORS, cookies, or redirects;
- verbose errors and logs that leak secrets;
- hardcoded credentials;
- unrestricted file upload;
- server-side template injection;
- XML external entities and SSRF;
- missing rate limits or weak randomness.

For each one, teach:

| Question | Example |
|---|---|
| What does the code look like? | `query = "SELECT * FROM users WHERE name = '" + name + "'"` |
| Why is it ordinary? | It is the shortest way to make the feature work |
| What does the attacker control? | `name` |
| What is the exploit endgame? | Change the query, bypass login, read data |
| What is the safe pattern? | Parameterised query |
| What is the one-line fix? | `cursor.execute("... WHERE name = %s", (name,))` |

See `references/bad-practices-to-exploits.md` for the full catalogue.

## Web-track essentials

Non-programmers need a small, concrete model of the web:

- A browser sends an **HTTP request**: method, URL, headers, cookies, body.
- A server sends an **HTTP response**: status, headers, body.
- **Client-side** code runs in the browser and is public.
- **Server-side** code runs where the data and permissions live.
- **Authentication** asks "who are you?"; **authorization** asks "are you
  allowed to do this?"
- A **session** or **token** is how the server remembers a user.
- A **parameter** is input; a **sink** is a dangerous place it can reach.
- A **database**, **shell**, **file path**, **template**, and **HTML page** are
  common sinks.
- A **status code** is a clue, not a full explanation.

Teach the request/response loop before teaching a framework.

## Software Security track progression

| Level | Learner can... | Programming knowledge needed |
|---|---|---|
| 1 | Read shipped JavaScript, find a hidden route, explain client-side trust | Variables, strings, comments, URLs, client vs server |
| 2 | Recognise input reaching a shell, craft a separator payload | Functions, parameters, strings, shell basics |
| 3 | Find missing authorization and session flaws | Requests, cookies, sessions, roles, identifiers |
| 4 | Triage a crash and write a first exploit script | Memory, pointers, buffers, offsets, Python basics |
| 5 | Build and document an end-to-end exploit | Everything above, plus mitigation reasoning |

Do not front-load OOP or architecture. Introduce a class only if the learner
must read one to find the bug. Introduce architecture only to show a trust
boundary, a proxy, a client/server split, or where a check is missing.

## Lab and workbook integration

- Give each lab a **bad-practice card**: pattern, attacker control, endgame,
  safe pattern, one-line fix.
- Put the **exploit endgame questions** in the lab objectives or analysis
  questions.
- Hints should scaffold: concept → observation → probe → payload. Never put the
  flag in the first hint.
- Workbook sections should include: Before You Begin → Scenario → Objectives →
  Background → Walkthrough → What Just Happened → Analysis Questions →
  Defensive Takeaways → If You Get Stuck.
- For beginner labs, offer a browser-only path and a terminal path. The terminal
  path is optional.
- Use the two DevFest starters as the model:
  [Hidden Export Route](../../../Workbook/CH_SWSEC_Software_Security/01_Hidden_Export_Route.md)
  and
  [Diagnostics Command Injection](../../../Workbook/CH_SWSEC_Software_Security/02_Diagnostics_Command_Injection.md).

## Safety and ethics

- All targets are fictional and isolated.
- The command-injection lab intentionally runs a shell inside its own container;
  say so, and say why that is not permission to attack anything else.
- Never include real personal data, real credentials, or live external targets.
- Teach disclosure: stop, report privately, and do not reuse a real secret.
- For memory-safety labs, use a local target and a crash/flag, not a real
  service.

## Review checklist

- [ ] The lesson answers the five exploit-endgame questions.
- [ ] The first explanation uses behaviour or an analogy, not syntax.
- [ ] OOP/architecture appears only when it explains a bug or boundary.
- [ ] The bad practice is named in plain language.
- [ ] The safe pattern and one-line fix are shown.
- [ ] The snippet is short and has one idea.
- [ ] The learner can succeed in the browser if the lab claims to be
      browser-only.
- [ ] Hints scaffold; the flag is not in the first hint.
- [ ] The workbook and lab test steps agree.
- [ ] No real data, credentials, or external targets.

## References

- `references/plain-language-concepts.md` — concept table, analogies, and what an
  attacker cares about.
- `references/bad-practices-to-exploits.md` — bad practice → exploit primitive →
  safe pattern.
- `references/teaching-patterns.md` — lesson templates, snippet rules, question
  ladders, and review workflow.
