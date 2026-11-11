# Exercise 2.6: Guided Cybersecurity Challenge

This is a bounded beginner challenge. You will combine the stage skills:

- preflight;
- service observation;
- one log clue;
- evidence notes;
- a short conclusion with confidence and an alternative explanation.

You will use only `curl`, `grep`, `cat`, and `ls`. You will not exploit, log in,
scan other ports, or contact another host.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Assigned target** | `challenge.lab:8080` for the Beginner Challenge lab. | **Yes. This is the only target in scope.** |

Open the **RangeBox Beginner Challenge** exercise. If the exercise panel shows a
different hostname or port, stop and ask. Do not scan to find another target.

### What you need

- [ ] The Beginner Challenge lab running.
- [ ] Your Target Card.
- [ ] Your evidence note template.
- [ ] About **25–35 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- complete a preflight before acting;
- observe one service without exploiting it;
- find one log clue and separate observation from interpretation;
- record reproducible evidence;
- write a short conclusion with confidence and an alternative explanation;
- stop when the target, data, or action is outside scope.

## The Scenario

A small community centre runs a practice web service. The service keeps a short
access log. Most requests are ordinary. One source made several failed requests,
then one request that should not have succeeded.

Your job is to:

1. confirm the target;
2. confirm the service answers;
3. read the log;
4. identify the repeated failures and the unusual success;
5. record the evidence;
6. explain what you can and cannot conclude;
7. submit the training flag.

This is a **defensive observation** exercise. You are not attacking the service.

## Approved Commands

Use only these commands:

```bash
curl -I http://challenge.lab:8080/access.log
curl http://challenge.lab:8080/access.log -o challenge.log
ls -l challenge.log
cat challenge.log
grep " 404 " challenge.log
grep " 200 " challenge.log
grep "OCR{" challenge.log
```

Do not add other tools, ports, hosts, or options. If a command is not listed,
ask before you use it.

## Walkthrough

### Step 1: Preflight

- [ ] Open the exercise panel.
- [ ] Confirm the target is `challenge.lab:8080`.
- [ ] Write it in your Target Card.
- [ ] Confirm the lab status is **Running**.
- [ ] Open the RangeBox terminal.

**Expected result:** a completed Target Card and a terminal prompt.

**Stop condition:** the target differs from the workbook, or no target is shown.
Stop and ask. Do not scan.

### Step 2: Observe the service

```bash
curl -I http://challenge.lab:8080/access.log
```

**Why:** this confirms that the service answers before you download the log. It
is a read-only check.

**Expected result:** an HTTP status line, such as `HTTP/1.1 200 OK`, and headers.

**Record:** status, protocol, hostname, and port. Do not claim a vulnerability
from the status.

### Step 3: Download the log

```bash
curl http://challenge.lab:8080/access.log -o challenge.log
ls -l challenge.log
```

**Why:** saving the log lets you search it without fetching it again.

**Expected result:** a non-empty `challenge.log`.

**If the file is empty:** check the lab status and target. Ask. Do not try
another host.

### Step 4: Read the log

```bash
cat challenge.log
```

**Why:** read before you filter. Look for the normal pattern first.

**Expected result:** several lines with source addresses, timestamps, requests,
status codes, and user agents.

### Step 5: Find the failures

```bash
grep " 404 " challenge.log
```

**Why:** repeated `404` requests may be probing, a broken link, or a retry. The
log alone does not prove intent.

**Record:**

| Question | Your answer |
|---|---|
| Which source made the repeated failures? | |
| Which paths did it try? | |
| How many failures? | |

### Step 6: Find the unusual success

```bash
grep " 200 " challenge.log
```

**Why:** a success after failures can be important. Read the request, the status,
and the user agent.

**Record:** the request, the source, and what made it unusual.

### Step 7: Find the training flag

```bash
grep "OCR{" challenge.log
```

**Why:** the flag is in the synthetic log. It is a training token.

**Expected result:** one line with `OCR{...}`. Copy the complete value into the
exercise panel.

### Step 8: Write the evidence note

```text
Timestamp:
Target: challenge.lab:8080
Action:
Result:
Meaning:
Next step:
Confidence:
Redactions:
```

Include:

- the preflight target;
- the service status;
- the repeated failures;
- the unusual success;
- the flag (submitted separately, not pasted into shared notes);
- what you can conclude;
- what you cannot conclude;
- one alternative explanation.

### Step 9: Write the conclusion

Use this structure:

1. **Observation:** what the log directly shows.
2. **Interpretation:** what you think it means.
3. **Confidence:** low, medium, or high, with a reason.
4. **Alternative explanation:** one other reasonable explanation.
5. **Next safe step:** record, ask, or stop.

**Example:**

> One source made three `404` requests to admin-style paths, then one `200`
> request with an unusual query string. This is consistent with probing, but it
> could also be a misconfigured client or a broken link. Confidence: medium. The
> next safe step is to record the evidence and ask the teacher whether the
> service owner expected this traffic.

## Staged Hints

Use a hint only after you have tried the step.

### Hint 1: Target and preflight

Check the exercise panel first. The target is `challenge.lab:8080`. If it differs,
stop. Do not scan.

### Hint 2: Service check

`curl -I` asks for headers only. A status line such as `200 OK` means the service
answered. It does not mean the service is vulnerable.

### Hint 3: Reading the log

Read the status codes first. `404` means the requested path was not found. `200`
means it was found. Look for a source that changes from failures to a success.

### Hint 4: Finding the flag

Search for the `OCR{` pattern in the log. Copy the complete value. Do not guess
or change it.

### Hint 5: Writing the conclusion

Separate what you saw from what you think. Add a confidence level and one
alternative explanation. Do not claim an attack from one log excerpt.

## Stop Conditions

Stop and ask your teacher if:

- the target differs from `challenge.lab:8080`;
- the log contains real personal information or a credential;
- you feel you need to scan another port or host;
- you feel you need to log in or exploit something;
- a command asks you to delete or change evidence;
- you are unsure whether an action is allowed.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong target | The exercise panel differs from the workbook | Stop and ask. Do not scan. |
| Lab not running | Status is not **Running** | Use **Start Exercise** or **Launch RangeBox**. |
| Name resolution failure | `Could not resolve host` | Check the spelling and exercise. Ask. |
| Empty log | No lines | Check the target and lab status. Ask. |
| No `404` lines | `grep` prints nothing | Check spacing and case. Read the log first. |
| No flag | `grep` prints nothing | Read the whole log. Do not guess. Ask if it is missing. |
| You are not sure what the log proves | A suspicious pattern | Write observation, confidence, and an alternative explanation. |

## Record Your Evidence

| Field | Your answer |
|---|---|
| Target | `challenge.lab:8080` |
| Service status | |
| Source of repeated failures | |
| Paths requested | |
| Unusual success | |
| Flag submitted? | Yes / No |
| Observation | |
| Interpretation | |
| Confidence | Low / Medium / High |
| Alternative explanation | |
| Next safe step | |
| What I did not do | (for example: no exploit, no login, no other ports) |

## What Success Looks Like

You are ready to finish when you can show:

- a completed preflight;
- a service check with the status recorded;
- a downloaded log;
- the repeated failures and the unusual success identified;
- the correct flag submitted;
- an evidence note with observation, interpretation, confidence, and an
  alternative explanation;
- a clear statement that you did not exploit, log in, or scan other ports.

## Key Takeaways

- Preflight first: target, status, terminal, notes.
- A service answering is not a vulnerability.
- Read the log before you filter it.
- Separate observation from interpretation.
- Confidence needs a reason, and every conclusion needs an alternative
  explanation.
- Stop when the target, data, or action is outside scope.
- The flag confirms completion, not an attack.

Next: [Troubleshooting, Reset, and Safe Exit](10_Troubleshooting_Reset_and_Safe_Exit.md).
