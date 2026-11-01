# Teaching Patterns for Non-Programmers

Use these patterns when authoring a lab, workbook page, hint, or classroom
explanation. The goal is confidence and code literacy, not programming
fluency.

## The 7-step lesson

1. **Show the feature.** What does the learner see and do?
2. **Show one input and output.** No code.
3. **Show the smallest code path.** 5–15 lines.
4. **Mark the trust boundary.** "This value came from the browser."
5. **Name the bad practice.** "The server pasted it into a shell."
6. **Try the smallest proof.** A request, payload, or crash.
7. **Show the safe version.** One sentence and one code change.

If a lesson starts with "first, a class is...", rewrite it.

## Three-pass code reading

### Pass 1 — Behaviour

Ask:

- What is the feature supposed to do?
- What does the user type or click?
- What comes back?

No code yet.

### Pass 2 — Data flow

Trace one value:

```text
input -> parameter -> function -> sink
```

At each step ask:

- Is this value controlled by the attacker?
- Is it checked?
- Is it encoded for this context?
- Is the check on the server or only in the browser?

### Pass 3 — Bad practice and endgame

Name the shortcut and answer:

1. What does the attacker control?
2. Where does it go?
3. What check is missing?
4. What is the impact?
5. How do you prove it?

## Exploit-endgame worksheet

Use this in the workbook or as an instructor prompt:

```text
Controlled input:
Entry point:
Path through the code:
Sink:
Missing/incorrect check:
Impact:
Smallest proof:
Safe pattern:
One-line fix:
```

## Analogy ladder

For every new term:

| Layer | Example: shell injection |
|---|---|
| Everyday | A sentence where a semicolon starts a second instruction |
| Technical | The application passes a string to `sh -c` |
| Code | `subprocess.run(f"getent {host}", shell=True)` |
| Consequence | `host = "127.0.0.1; cat /tmp/flag"` runs two commands |

Use one analogy per concept. Do not stack three metaphors.

## Snippet rules

- 5–15 lines.
- One idea.
- Show input, dangerous line, output.
- Prefer standard-library code.
- Avoid frameworks, ORMs, decorators, and metaprogramming in the first pass.
- Put the unsafe and safe versions side by side.
- Highlight one line in prose.

### Unsafe/safe pair template

```python
# Unsafe
query = "SELECT * FROM users WHERE name = '" + name + "'"

# Safe
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

Ask: "What changed?" The answer should be "the data is no longer part of the
query text."

## Hint ladder

Hints should move from concept to proof, never straight to the flag.

1. **Concept hint:** what kind of bug to look for.
2. **Observation hint:** where to look (page, source, parameter, response).
3. **Probe hint:** a harmless test (`; id`, a quote, a changed ID).
4. **Payload hint:** the shape of the working input, without the flag.

Do not put the flag in hint 1. Do not put the full payload in hint 1.

## Question ladder for learners

Use these to check understanding without a quiz:

1. **Recall:** "What did you type?"
2. **Explain:** "Why did that change the command/query?"
3. **Locate:** "Which line trusted the input?"
4. **Fix:** "What would you change?"
5. **Test:** "What request would prove the fix?"
6. **Transfer:** "Where else in this app could the same pattern appear?"

## Bridging OOP and architecture

When the learner asks about classes or architecture, answer in service of the
bug:

- "You do not need the whole class. You need this method and the value it
  trusts."
- "The class does not make it safe. The method still pastes input into SQL."
- "The architecture matters here because the browser is public and the server
  holds the database. The check must be on the server."
- "The proxy matters because it normalises the path before the app checks it."

Do not turn the answer into a design lecture. Return to the data flow.

## Common non-programmer pitfalls

| Pitfall | Better move |
|---|---|
| Starting with syntax | Start with the visible behaviour |
| Defining every term | Define only the term needed for this bug |
| Showing a 100-line file | Show the 8 lines on the path |
| "It's obvious" | Say what to look at and why |
| Teaching OOP first | Teach input, trust, and sinks first |
| Using framework magic | Use a standard-library example |
| Confusing authentication and authorization | Ask "who are you?" then "are you allowed?" |
| Treating a status code as the whole answer | Explain the request and response |
| Giving the payload in hint 1 | Scaffold concept → observation → probe → payload |
| Assuming a terminal | Provide a browser-only path |

## Assessment rubric

A learner has met the objective when they can:

- [ ] describe the feature in plain language;
- [ ] point to the input they control;
- [ ] trace it to the sink;
- [ ] name the missing check or bad practice;
- [ ] demonstrate a minimal proof;
- [ ] explain the impact;
- [ ] describe the safe pattern;
- [ ] suggest one test for the fix.

They do **not** need to write a full program or explain OOP.

## Lab review workflow

1. Read the lab as a non-programmer.
2. Identify the one bad practice.
3. Fill the exploit-endgame worksheet.
4. Check the hint ladder.
5. Check the browser-only path if claimed.
6. Check the safe pattern is concrete.
7. Check the workbook and test steps match the flag.
8. Remove any sentence that exists only to show off jargon.

## Web-track pattern

For a Web lab, add:

- a request/response example;
- a client-side vs server-side note;
- the parameter and sink;
- one browser-only proof;
- the authorization or validation fix.

## Software-security pattern

For a Software Security lab, add:

- the bad-practice card;
- the exploit-endgame worksheet;
- a minimal proof;
- the safe pattern;
- a transfer question: "Where else could this pattern appear?"

## Memory-safety pattern (Level 4+)

Do not use this for a beginner DevFest lab. When you do:

- start with the memory model (numbered boxes, fixed-size buffer, pointer);
- show a normal input and a too-long input;
- show the crash;
- explain the saved return address or function pointer;
- write the exploit script in small steps;
- discuss canaries, NX, and ASLR as changes to the path, not trivia.

## Review checklist

- [ ] The lesson answers the five exploit-endgame questions.
- [ ] The first explanation is behaviour or analogy, not syntax.
- [ ] OOP/architecture appears only when it explains a boundary or bug.
- [ ] The bad practice is named in plain language.
- [ ] The safe pattern and one-line fix are concrete.
- [ ] The hint ladder does not start with the payload or flag.
- [ ] The browser-only claim is true.
- [ ] The workbook and test steps agree.
- [ ] No real data, credentials, or external targets.
