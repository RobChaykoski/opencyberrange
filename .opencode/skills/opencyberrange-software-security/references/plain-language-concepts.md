# Plain-Language Programming Concepts

Use this reference when a learner needs to read a small piece of code but does
not need to become a programmer. The goal is **code literacy for exploitation**,
not language fluency.

## How to use this table

For each concept, give the learner:

1. the everyday analogy;
2. the technical word;
3. one code line where it matters;
4. why an attacker cares.

Do not teach the whole language. Teach the concept only when it appears in the
bug being studied.

## Core concepts

| Concept | Plain meaning | Analogy | Why an attacker cares | Show this |
|---|---|---|---|---|
| Variable | A named box that holds a value | A labelled locker | If the attacker can change the value, they change the program's behaviour | `name = request.args["name"]` |
| String | Text | A sentence | Most injection bugs start with text that is treated as code | `"Hello, " + name` |
| Integer | A whole number | A counter | Sizes, counts, IDs, and offsets can overflow or be negative | `size = int(input)` |
| Boolean | True/false | A light switch | A single `is_admin = True` can decide access | `if user.is_admin:` |
| Array/list | An ordered collection | A row of mailboxes | Index errors and out-of-bounds reads are memory bugs | `items[5]` |
| Object/class | A bundle of data and functions | A form with fields and instructions | A class is not a security boundary; its methods can still trust input | `user.role` |
| Function | A named action | A recipe step | The dangerous line usually lives inside a function | `def lookup(host):` |
| Parameter | Input to a function | An ingredient | Parameters are where untrusted data enters | `def search(query):` |
| Return value | What a function gives back | The finished dish | The return value may be trusted later without checking | `return run(query)` |
| Condition | A decision | A fork in the road | Missing or inverted conditions cause authorization bugs | `if not user.is_admin: deny()` |
| Loop | Repeat an action | An assembly line | Off-by-one and unbounded loops cause crashes or resource abuse | `for i in range(n):` |
| Input | Data from outside | A form at a front desk | The attacker controls this | `request.form["host"]` |
| Output | Data sent back | A notice board | Output can leak data or execute in the wrong context | `return f"<p>{name}</p>"` |
| Trust boundary | Where data changes owner | A door between departments | Checks must happen at the boundary, not only in the browser | browser → server |
| Validation | Checking input is allowed | A guest list | Missing validation lets unexpected values through | `if not re.match(...)` |
| Encoding | Making data safe for a context | Packing a parcel correctly | Wrong encoding turns data into code | HTML, SQL, shell, URL |
| Database | Organised stored data | A filing cabinet | Queries can be changed to read or modify other records | `SELECT ... WHERE id = ?` |
| Query | A request to the database | A question to the filing clerk | String-built queries are SQL injection | `"... WHERE name = '" + name + "'"` |
| Shell | A command interpreter | A sentence where punctuation changes meaning | User input in a shell becomes extra commands | `sh -c "getent " + host` |
| File path | A location on disk | A street address | `../` can escape the intended folder | `open(root + name)` |
| HTTP request | Browser asks the server for something | A order slip | Method, URL, headers, cookies, and body are all input | `GET /lookup?host=...` |
| HTTP response | Server's answer | The delivered parcel | Status, headers, and body reveal behaviour and data | `200 OK`, `403`, `500` |
| Cookie/session | Server remembers a user | A wristband at an event | A stolen or forged session becomes another user | `session["user_id"]` |
| Token | A value that stands in for identity or permission | A ticket | Secrets in client code are public tickets | `?token=...` |
| Authentication | Who are you? | Showing ID | Bypassing it gives any account | login check |
| Authorization | Are you allowed? | A door that opens only for some badges | Missing checks expose other users' data | `if record.owner != user:` |
| Hash | A one-way fingerprint | A paper shredder with a receipt | Weak password hashes can be cracked | `sha256(password)` |
| Encryption | Reversible hiding | A locked box | A leaked key defeats it | `Fernet.decrypt(...)` |
| Serialization | Turning data into a format | Packing a parcel | Deserialising untrusted data can run code | `pickle.loads(data)` |
| Memory/pointer | Numbered storage and an address label | Lockers and a label with a locker number | Wrong addresses corrupt data or control flow | `char buf[8]; strcpy(buf, input);` |
| Buffer | A fixed-size box | An eight-slot tray | Too much data spills into neighbouring memory | `strcpy`, `gets`, `sprintf` |
| Stack/heap | Where temporary and dynamic data live | Workbench vs warehouse | Overflow location changes the exploit path | stack canary, heap metadata |
| Race condition | Two actions interleave badly | Two clerks editing one file | A check can be true, then false before use | TOCTOU |
| Error/log | A message about failure | A note in a logbook | Verbose errors leak paths, queries, and secrets | stack trace |

## Builder knowledge vs breaker knowledge

### Object-oriented programming

OOP is about grouping data and behaviour into classes. It helps programmers
organise large systems. It is **not** a security property.

For an exploit, ask:

- Does this method trust a parameter?
- Does this subclass override a check?
- Is `is_admin` a field the user can set?
- Does the object load state from an untrusted source?
- Can a method be called in an order the designer did not expect?

Do not teach inheritance trees or design patterns unless the learner must read
one to find the bug.

### Architecture

Architecture is about how components are arranged: browser, API, worker,
database, cache, proxy, queue, storage.

For an exploit, architecture matters only where it creates a **trust boundary**
or a **reachable sink**:

- Where does the request cross from public to private?
- Which service performs the authorization check?
- Does the proxy normalise the path before the app checks it?
- Can the app reach an internal service or database?
- Does the queue carry untrusted data to a privileged worker?

Do not teach layered architecture, microservices, or design patterns as a
prerequisite. Use a simple box-and-arrow diagram only when the bug depends on
the boundary.

## Three-pass code reading

### Pass 1: Behaviour

What does the learner see? What does the feature promise? No code yet.

### Pass 2: Data flow

Trace one input from the browser to the sink:

```text
form field -> request parameter -> function argument -> shell/database/file
```

Mark each stop with: **controlled by attacker? checked? trusted?**

### Pass 3: Bad practice

Name the shortcut:

- "The query is built by pasting strings together."
- "The server passes the hostname to a shell."
- "The page hides the admin link but the server does not check the role."

Then ask the five exploit-endgame questions from `SKILL.md`.

## Minimal web model for non-programmers

```text
Browser (public)  --request-->  Server (private data, permissions)
Browser (public)  <--response--  Server
```

- The browser can be inspected and changed.
- The server is where authorization must happen.
- A parameter is input; a sink is where it can do damage.
- A hidden link, disabled button, or client-side check is not security.

## Minimal memory model for later levels

- Memory is a row of numbered boxes.
- A buffer is a fixed-size group of boxes.
- A pointer is a label with a box number.
- Writing past the end of a buffer changes neighbouring boxes.
- The exploit goal is to control what the program reads or executes next.
- Stack canaries, NX, and ASLR are mitigations that change the exploit path.

Teach this only at Level 4. Do not put it in a beginner DevFest lab.

## Vocabulary card template

```text
Word:
Plain meaning:
Analogy:
Where it appears in this lab:
Why an attacker cares:
One-line safe pattern:
```

Use the card in the workbook or as a hint, not as a glossary dump.
