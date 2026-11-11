# Exercise W1.10: Reconnaissance Findings and Attack-Surface Map

## Before You Begin

This exercise turns notes from W1.1–W1.9 into a defensible application map. It
does not send new traffic. Use only evidence you already collected from the
approved lab targets.

No credentials are required. Do not add a target, route, or payload to make the
map look more complete.

## Words to Know

| Term | Meaning |
|---|---|
| **Attack surface** | The reachable hosts, routes, inputs, identities, and data an application exposes. |
| **Finding** | A recorded observation with evidence, interpretation, confidence, and limits. |
| **Evidence** | The exact URL, request, response, timestamp, or screenshot that supports a statement. |
| **Confidence** | How strongly the evidence supports the interpretation: Low, Medium, or High. |
| **Limitation** | What the evidence does not prove. |
| **Observed** | You saw a request or response. |
| **Discovered** | A name or path exists in a list or response. |
| **Reachable** | A request receives a response. |
| **Authenticated** | An identity is proven to the application. |
| **Authorized** | The application permits that identity to perform the action. |
| **Sensitive** | Data that would cause harm if exposed. |
| **Misconfigured** | A control is missing or weak; exploitability is not yet proven. |
| **Confirmed vulnerable** | A safe, authorized test demonstrated impact. |

## Walkthrough

### Step 1: Assemble the evidence set

Gather the evidence tables from W1.1–W1.9. For each item, confirm you have:

- the exact URL and method;
- the target hostname and port;
- the status code and relevant response headers;
- a timestamp;
- the observation, interpretation, confidence, and limitation;
- the redactions you applied.

If an item has no evidence, remove it from the map or mark it **Unverified**.

### Step 2: Build the attack-surface map

Create a table with these columns:

| Host | Route | Method | Input | Authentication | Role | Technology evidence | Data type | Confidence |
|---|---|---|---|---|---|---|---|---|
| `target.lab` | `/` | `GET` | None | None observed | None observed | | Public page | Medium |
| | | | | | | | | |

Rules:

- One row per host, route, and method combination.
- Put a value in every cell. Use `None observed` or `Unknown`, not a blank.
- Keep technology evidence to clues you corroborated.
- Do not list a route you did not request.

### Step 3: Classify each row

Use the ladder, not a single label:

| State | Question |
|---|---|
| Observed | Did I see the request or response? |
| Discovered | Did a wordlist, link, or file name the resource? |
| Reachable | Did the server return a response? |
| Authenticated | Did the application prove an identity? |
| Authorized | Did the application permit the action for that identity? |
| Sensitive | Would the returned data cause harm if exposed? |
| Misconfigured | Is a control missing or weak? |
| Confirmed vulnerable | Did a safe test demonstrate impact? |

A reachable page is not automatically authorized, sensitive, or vulnerable.

### Step 4: Write one finding

Use this structure for the most important observation:

| Field | Your note |
|---|---|
| Finding ID | F-01 |
| Title | |
| Exact URL | |
| Method | |
| Request evidence | |
| Response evidence | |
| Timestamp | |
| Observation | |
| Interpretation | |
| Confidence | Low / Medium / High |
| Limitation | |
| Next safe test | |
| Redactions | |

Write the title as an observation, not a conclusion. For example:
"Diagnostic header names an internal path" is safer than "Path traversal
vulnerability".

### Step 5: Redact and review

Before sharing:

- remove cookies, tokens, passwords, personal data, and internal addresses;
- crop screenshots to the relevant request or header;
- keep the timestamp and target visible;
- ask a peer to state what each finding proves and what it does not.

## Evidence

| Field | Your note |
|---|---|
| Number of map rows | |
| Hosts represented | |
| Rows with confirmed authorization | |
| Rows with sensitive data | |
| Findings written | |
| Redactions applied | |
| Peer review completed? | Yes / No |

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| A row has no evidence | Remove it or mark it Unverified. |
| You cannot tell authorized from reachable | Record `Authorization not tested` and stop. |
| Two tools disagree | Keep both observations and lower confidence. |
| A finding sounds like a vulnerability | Reword it as an observation unless impact was demonstrated. |
| You want to test a new route | Do not. This exercise only organizes existing evidence. |

## What Success Looks Like

You can show a complete map with no blank cells, one finding with exact
evidence and a limitation, one classification that separates reachable from
authorized, and a redacted evidence set. This exercise has **no flag**.
