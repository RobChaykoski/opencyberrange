# Logs and Event Review

This activity uses a small synthetic web access log. You will identify **who,
what, when, where, and result**, separate observation from interpretation, and
explain why one failed event does not prove an attack.

The log is fictional. Do not investigate classmates, real school systems, or
real personal data.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Assigned target** | `events.lab:8080` for the Log Review lab. | **Yes. This is the only target in scope.** |

Open the **RangeBox Log Review** exercise. If the exercise panel shows a
different hostname or port, stop and ask.

### What you need

- [ ] The Log Review lab running.
- [ ] The RangeBox terminal open.
- [ ] A notes file for the evidence table.
- [ ] About **20–30 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- define log, event, timestamp, severity, source, user, process, success,
  failure, and false positive;
- identify who, what, when, where, and result in a log line;
- explain time zones, repeated events, and missing context;
- explain why one failed event does not prove an attack;
- redact credentials and personal information;
- record observation, interpretation, confidence, and an alternative
  explanation.

## Words to Know

| Term | What it means |
|---|---|
| **Log** | A record of events written by a system or application. |
| **Event** | One thing that happened, such as a request or a login attempt. |
| **Timestamp** | The date and time recorded for an event. |
| **Severity** | How serious an event is labelled, such as info, warning, or error. |
| **Source** | Where the event came from, such as an IP address or application. |
| **User** | The account associated with an event, if one is recorded. |
| **Process** | The program that produced or handled the event. |
| **Success** | The action completed, often shown by a status such as `200`. |
| **Failure** | The action did not complete, often shown by a status such as `404`. |
| **False positive** | Something that looks suspicious but has a benign explanation. |

## Reading a Web Access Log

A log line may look like this:

```text
SOURCE_IP - - [18/Mar/2026:09:12:10 +0000] "GET /admin HTTP/1.1" 404 189 "-" "sqlmap/1.8"
```

Read it in fields:

| Field | Example | Question |
|---|---|---|
| Source | `SOURCE_IP` | Who made the request? |
| Timestamp | `18/Mar/2026:09:12:10 +0000` | When did it happen? |
| Request | `GET /admin HTTP/1.1` | What was requested? |
| Status | `404` | What was the result? |
| Bytes | `189` | How large was the response? |
| User agent | `sqlmap/1.8` | What client identified itself? |

The **who** is a source address, not necessarily a person. The **where** is the
service that wrote the log. The **result** is the status code.

## Walkthrough

### Step 1: Download the log

```bash
curl http://events.lab:8080/access.log -o access.log
ls -l access.log
```

**Why:** saving the log lets you search it without fetching it again.

**Expected result:** a file named `access.log` with several lines.

**If the file is empty:** check that the lab is running and the target is
`events.lab:8080`. Do not try another host.

### Step 2: Read the first few lines

```bash
cat access.log
```

**Why:** read before you filter. You need to see the normal pattern.

**Expected result:** several log lines with ordinary page views and some failed
requests.

### Step 3: Count the status codes

```bash
grep -c " 200 " access.log
grep -c " 404 " access.log
```

**Why:** `grep -c` counts matching lines. The spaces around `200` and `404` make
the match more specific.

**Expected result:** two numbers. A normal page view returns `200`; a missing
page returns `404`.

**If a count is zero:** read the log again and check the spacing. Do not change
the log.

### Step 4: Find the repeated failures

```bash
grep " 404 " access.log
```

**Why:** repeated failures from one source may be a broken link, a typo, a
scanner, or probing. The log alone does not tell you which.

**Expected result:** several failed requests, possibly from the same source.

**Record:**

| Question | Your answer |
|---|---|
| Which source made the repeated failures? | |
| Which paths did it try? | |
| How many failures? | |

### Step 5: Find the unusual success

```bash
grep " 200 " access.log
```

**Why:** a success after repeated failures can be important, but it is not proof
of an attack. Read the request and the user agent.

**Expected result:** normal page views and one request with an unusual query
string.

### Step 6: Find the training token

```bash
grep "OCR{" access.log
```

**Why:** the flag is in the synthetic log. It is a training token, not a real
secret.

**Expected result:** one line with `OCR{...}`. Copy the complete value into the
Log Review exercise panel.

### Step 7: Separate observation from interpretation

Write two columns in your notes:

| Observation | Interpretation |
|---|---|
| One source made several `404` requests. | The source may have been probing, or it may have followed a broken link. |
| The same source later received `200`. | The request succeeded. It does not prove the request was authorized. |
| The user agent identifies a scanning tool. | The client claimed that identity. It is a clue, not proof. |

**Why:** an observation is what the log says. An interpretation is what you think
it means. Keep them separate.

### Step 8: Consider missing context

Ask:

- What happened before the first line?
- What happened after the last line?
- Were other logs available?
- Was this source seen before?
- Was the request expected by the service owner?

A log excerpt is not the whole story. One failed event does not prove an attack.
One successful event does not prove compromise.

## Time Zones and Repeated Events

- The example timestamp ends with `+0000`, which means UTC.
- Your desktop clock may show a different local time.
- Do not compare timestamps from different time zones without converting.
- Repeated events may be a scheduled job, a retry, a broken link, or a scan.
- Count the repeats before you decide what they mean.

## Redaction and Privacy

- Do not copy passwords, tokens, personal information, or full URLs with
  sensitive query strings into shared notes.
- The training token in this lab is safe to submit to the exercise panel.
- If a log contains a real credential, stop and tell your teacher. Do not share
  it.
- Do not investigate classmates or real school systems.
- Redact names, email addresses, and account details when you describe the event.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong target | The exercise panel differs from the workbook | Stop and ask. Do not fetch another log. |
| Empty log | `access.log` has no lines | Check the lab status and target. Ask. |
| No matches | `grep` prints nothing | Check spacing and case. Read the log first. |
| Timestamp confusion | A time does not match your clock | Check the time zone. Do not change the log. |
| You think you found an attack | One suspicious line | Record the observation, confidence, and an alternative explanation. Ask. |
| Sensitive data appears | A real-looking password or personal detail | Stop. Do not copy or share. Tell your teacher. |

## Record Your Evidence

| Field | Your answer |
|---|---|
| Target | `events.lab:8080` |
| Log file | `access.log` |
| Who (source) | |
| What (request) | |
| When (timestamp and time zone) | |
| Where (service) | |
| Result (status) | |
| Observation | |
| Interpretation | |
| Confidence | Low / Medium / High |
| Alternative explanation | |
| Next safe step | |

Then answer:

1. What is the difference between a log and an event?
2. What does a timestamp tell you?
3. What does a `404` mean?
4. Why does one failed event not prove an attack?
5. Why can repeated events be normal?
6. What is a false positive?
7. Why must you separate observation from interpretation?
8. What should you do if a log contains a real credential?

## What Success Looks Like

You are ready to continue when you can show:

- a downloaded log;
- counts of successful and failed requests;
- one repeated pattern identified;
- one observation and one interpretation, clearly separated;
- one alternative explanation;
- one confidence level;
- the lab flag submitted;
- a clear statement that one event is not a conclusion.

This activity uses the **Log Review** lab flag (`OCR{...}` in the log). The flag
confirms that you found the synthetic token, not that you proved an attack.

## Key Takeaways

- A log records events; an event is one thing that happened.
- Read who, what, when, where, and result.
- A failed event can be a typo, a broken link, a retry, or a scan.
- Repeated events need context and a baseline.
- An open or successful request is not automatically malicious.
- Separate observation from interpretation.
- Record confidence and an alternative explanation.
- Redact credentials and personal information.

Next: [Evidence Notes and Technical Communication](08_Evidence_Notes_and_Technical_Communication.md).
