# Chapter Review

This is the readiness gate for **Beginner Stage 2**. It checks whether you can
work safely, explain evidence, and choose a safe next step. It is not a speed
test and not a grade.

You do not need to memorise commands. You need to know what to use, where to use
it, and when to stop.

## Before You Begin

### Where to run this review

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, for reading and notes. |
| **Notes file** | Your own notes, outside RangeBox. | **Yes. Write your answers here.** |
| **RangeBox terminal** | The text window inside RangeBox. | Only if you choose to try a reference command. |
| **Assigned target** | A target named in an exercise. | **This review has no target of its own.** Use only the target in your current exercise. |

This review has **no required commands** and **no flag**. The reference at the
end is for your notes and later practice.

### How this review works

- **Matching:** connect a term to its meaning.
- **Sequencing:** put steps in a safe order.
- **Command interpretation:** read output and identify what it shows.
- **Evidence classification:** decide whether a statement is observation,
  interpretation, or unsupported.
- **Scenario:** choose a safe action.
- **Remediation:** the page to revisit if a skill is not ready.

No trick questions. If something is unclear, write what you would check or who
you would ask.

## Part 1: Matching

Match each term with one meaning.

| # | Term | Letter | Meaning |
|---|---|---|---|
| 1 | Executable | | A. A setting that changes how a command works, often starting with `-`. |
| 2 | Option | | B. The normal output a command prints. |
| 3 | Argument | | C. A number a command returns; `0` usually means success. |
| 4 | Standard output | | D. The program a command name starts. |
| 5 | Standard error | | E. Sends one command's output into another command. |
| 6 | Pipe | | F. A socket waiting for incoming connections. |
| 7 | Exit status | | G. Extra information a command acts on, such as a file name. |
| 8 | Permission string | | H. Something that looks suspicious but has a benign explanation. |
| 9 | Listener | | I. The ten-character permission code from `ls -l`. |
| 10 | False positive | | J. Error messages a command prints. |

## Part 2: Sequencing

### A. Command cycle

Put these in order.

| Order | Step |
|---|---|
| | Execute the command. |
| | Correct one thing if the result differs. |
| | Predict what will happen. |
| | Verify the result against the prediction. |

### B. Safe recovery

Put these in order, from least to most disruptive.

| Order | Step |
|---|---|
| | Read the error and check `pwd`, `whoami`, and `ls`. |
| | Save notes outside RangeBox. |
| | Try **Reconnect** or **Open RangeBox**. |
| | Use **Stop Exercise** or **Stop RangeBox**, then relaunch. |
| | Ask your teacher after two safe steps fail. |

## Part 3: Command Interpretation

### A. Permission line

```text
-rw-------  1 kali kali  42 Nov 11 10:00 note.txt
```

1. Is this a file or a folder?
2. What can the owner do?
3. What can the group do?
4. What can other users do?
5. What numeric mode matches this line?

### B. Process output

```text
PID   PPID  COMMAND
4242  4100  bash
```

1. Which number is the process ID?
2. Which number is the parent process ID?
3. What program is running?
4. Is this a listener? How do you know?

### C. Socket output

```text
State   Local Address:Port   Peer Address:Port
LISTEN  0.0.0.0:8080         0.0.0.0:*
```

1. What state is shown?
2. What port is listening?
3. Is this a client connection or a listener?
4. Does this prove a vulnerability?

### D. Scan output

```text
PORT     STATE SERVICE VERSION
8080/tcp open  http    <service version>
```

1. Which host and port were scanned?
2. What is the state?
3. What service label is shown?
4. What can you conclude?
5. What can you not conclude?

### E. Log line

```text
SOURCE_IP - - [18/Mar/2026:09:12:10 +0000] "GET /admin HTTP/1.1" 404 189 "-" "sqlmap/1.8"
```

1. Who made the request?
2. What was requested?
3. When did it happen?
4. What was the result?
5. Does this one line prove an attack? Why not?

## Part 4: Evidence Classification

Mark each statement **Observation**, **Interpretation**, or **Unsupported**.

| Statement | Your answer |
|---|---|
| The output says `HTTP/1.1 200 OK`. | |
| The service is vulnerable because port 8080 is open. | |
| Port 8080 is open. | |
| One source made three `404` requests. | |
| The source was attacking the site. | |
| The log excerpt does not show what happened before it. | |

## Part 5: Scenarios

### Scenario 1: Target mismatch

The exercise panel shows `challenge.lab` on port `9090`. Your workbook page says
`challenge.lab` on port `8080`.

### Scenario 2: Permission denied

You run `cd folder` and see `Permission denied`. `ls -ld folder` shows
`drw-------`.

### Scenario 3: No network response

`curl -I http://network.lab:8080/status.json` hangs with no output.

### Scenario 4: One failed event

A log shows one `404` request from an unknown source. A classmate says, "That
proves an attack."

### Scenario 5: Screenshot

You want to screenshot a terminal that contains a password and a token.

### Scenario 6: Open port

A scan shows `8080/tcp open http`. A classmate says, "The server is hacked."

### Scenario 7: Authorization

You can reach another student's lab target. It is not your assigned target.

### Scenario 8: Cleanup

You downloaded `access.log` and `challenge.log` into your home folder. You are
finished.

## Part 6: One-Page Reference

### Safe commands

| I need to… | Command | Replace or option |
|---|---|---|
| Find my folder | `pwd` | Nothing. |
| Find my account | `whoami` | Nothing. |
| List files | `ls` | Nothing. |
| See permissions | `ls -l FILE` | Replace `FILE`. |
| Create a folder | `mkdir -p FOLDER` | `-p` means no error if it exists. |
| Enter a folder | `cd FOLDER` | Replace `FOLDER`. |
| Read a file | `cat FILE` | Replace `FILE`. |
| Search text | `grep "TEXT" FILE` | Replace `TEXT` and `FILE`. |
| Count matches | `grep -c "TEXT" FILE` | `-c` counts lines. |
| Show my shell process | `ps -o pid,ppid,comm -p $$` | Nothing. |
| List listening sockets | `ss -tuln` | `-t` TCP, `-u` UDP, `-l` listening, `-n` numeric. |
| Check one service | `curl -I http://TARGET:PORT/PATH` | `-I` is headers only. |
| Bounded service check | `nmap -sV -p PORT TARGET` | One host, one port. |
| Change a practice file mode | `chmod 600 FILE` | Only in your practice folder. |
| Remove one file | `rm FILE` | Exact name only. |
| Remove one empty folder | `rmdir FOLDER` | Empty only. |

**Never** use `sudo`, `chown`, `rm *`, `rm -r`, `rm -rf`, or a scan against a
range, subnet, or public address.

### Evidence template

```text
Timestamp:
Target:
Action:
Result:
Meaning:
Next step:
Confidence:
Redactions:
```

### Key terms

| Term | Meaning |
|---|---|
| Process | A running instance of a program. |
| PID | The number that identifies a process. |
| Service | A program that provides something, often over a network. |
| Listener | A socket waiting for connections. |
| Port | A number that identifies a service. |
| Enumeration | Observing what a service exposes. |
| Log | A record of events. |
| Evidence | Information that supports a statement. |
| Confidence | How strongly evidence supports an interpretation. |
| False positive | A benign explanation for a suspicious-looking event. |
| Authorization | Permission for a specific action on a specific system. |
| Redaction | Hiding or removing sensitive details. |

### Help steps

1. Read the step again.
2. Open the **Hint**.
3. Write the step, expected result, and actual result.
4. Ask your teacher. Do not share a password.
5. Stop if you feel unsafe.

### Stop conditions

Stop and ask if:

- the target differs from the workbook;
- you see another student's data;
- a credential may be exposed;
- a browser security warning appears;
- you are asked to scan outside the exercise;
- you are unsure whether an action is allowed;
- you are unsure whether a file is safe.

## Part 7: Confidence Reflection

Not graded. Mark one box for each statement.

| I can… | Not yet | Almost | Yes |
|---|---|---|---|
| Complete a RangeBox preflight. | [ ] | [ ] | [ ] |
| Explain a command, option, argument, pipe, and redirection. | [ ] | [ ] | [ ] |
| Read a permission string and numeric mode. | [ ] | [ ] | [ ] |
| Connect an application, process, service, and port. | [ ] | [ ] | [ ] |
| Explain listening, established, closed, filtered, and unreachable. | [ ] | [ ] | [ ] |
| Perform one bounded service observation. | [ ] | [ ] | [ ] |
| Read a log and separate observation from interpretation. | [ ] | [ ] | [ ] |
| Write a reproducible evidence note. | [ ] | [ ] | [ ] |
| Explain authorization and redact sensitive data. | [ ] | [ ] | [ ] |
| Troubleshoot, reset, and clean up safely. | [ ] | [ ] | [ ] |
| Ask for help without sharing a password. | [ ] | [ ] | [ ] |

## Part 8: Readiness Checklist

- [ ] I completed the matching, sequencing, interpretation, evidence, and
      scenario sections.
- [ ] I can explain my answers in my own words.
- [ ] I know where the target appears and what to do on a mismatch.
- [ ] I know why an open port is not a vulnerability.
- [ ] I know why one log line is not a conclusion.
- [ ] I know how to save notes and clean up.
- [ ] I know how to stop the lab and log out on a shared device.
- [ ] I have not shared a password or real personal information.

## Remediation Pointers

| Skill | Page |
|---|---|
| Preflight and target | [RangeBox Review and Preflight](01_RangeBox_Review_and_Preflight.md) |
| Command line | [Command Line Fluency](02_Command_Line_Fluency.md) |
| Permissions | [Files, Permissions, and Ownership](03_Files_Permissions_and_Ownership.md) |
| Processes and services | [Processes, Services, and Applications](04_Processes_Services_and_Applications.md) |
| Network connections | [Network Communication and Ports](05_Network_Communication_and_Ports.md) |
| Enumeration | [Introductory Service Enumeration](06_Introductory_Service_Enumeration.md) |
| Logs | [Logs and Event Review](07_Logs_and_Event_Review.md) |
| Evidence notes | [Evidence Notes and Technical Communication](08_Evidence_Notes_and_Technical_Communication.md) |
| Challenge | [Guided Cybersecurity Challenge](09_Guided_Cybersecurity_Challenge.md) |
| Troubleshooting | [Troubleshooting, Reset, and Safe Exit](10_Troubleshooting_Reset_and_Safe_Exit.md) |
| Stage 1 ethics | [Cyber Ethics, Privacy, and Digital Citizenship](../CH_HS09_Grade_9_RangeBox_Basics/08_Cyber_Ethics_Privacy_and_Digital_Citizenship.md) |

## Answers and Explanations

Cover this section until you finish Parts 1–5.

### Part 1: Matching

1-D, 2-A, 3-G, 4-B, 5-J, 6-E, 7-C, 8-I, 9-F, 10-H.

### Part 2: Sequencing

**A. Command cycle:** 1 — Predict. 2 — Execute. 3 — Verify. 4 — Correct.

**B. Safe recovery:** 1 — Read the error and check context. 2 — Try
**Reconnect** or **Open RangeBox**. 3 — Save notes before a reset. 4 — Stop and
relaunch. 5 — Ask your teacher. Saving notes can happen before or during the
recovery; the key is to save before the reset.

### Part 3: Command interpretation

**A.** It is a file (`-`). Owner can read and write (`rw-`). Group and other have
no permissions (`---`). The numeric mode is `600`.

**B.** PID is `4242`; PPID is `4100`; the program is `bash`. It is not a listener;
there is no socket state or port.

**C.** `LISTEN`; port `8080`; it is a listener, not a client connection. It does
not prove a vulnerability.

**D.** One host and port `8080`; state `open`; service `http`; the service
answered. You cannot conclude that it is vulnerable from the state and label.

**E.** Source is `SOURCE_IP`; request `/admin`; time `18/Mar/2026:09:12:10
+0000`; result `404`. One line does not prove an attack; it could be a typo, a
broken link, a scanner, or a retry.

### Part 4: Evidence classification

1. Observation.
2. Unsupported.
3. Observation.
4. Observation.
5. Interpretation with low confidence.
6. Observation about missing context.

### Part 5: Scenario guidance

1. **Target mismatch:** stop. Do not try either port. Write both values and ask.
2. **Permission denied:** `drw-------` has no owner execute. Add owner execute
   with `chmod 700 folder`, then try again. This is your practice folder only.
3. **No network response:** wait about 10 seconds, press `Ctrl` + `C`, check the
   lab status and target. Try **Reconnect** or **Open RangeBox**. Do not scan.
4. **One failed event:** one `404` is not proof. Ask for the surrounding log,
   baseline, and service owner context. Record low confidence.
5. **Screenshot:** do not capture the password or token. Redact them or use
   copied text. Tell your teacher if a credential was exposed.
6. **Open port:** an open port is a service accepting connections, not a
   compromise. Do not claim a vulnerability from the scan.
7. **Authorization:** do not use it. It is not your assigned target.
8. **Cleanup:** `pwd`, `ls`, then `rm access.log challenge.log`; verify with
   `ls`. Do not use a wildcard.

## What Success Looks Like

You can show:

- completed matching, sequencing, interpretation, evidence, and scenario answers;
- one explanation of a target mismatch and the stop rule;
- one explanation of why an open port is not a vulnerability;
- one explanation of why one log line is not a conclusion;
- one evidence note or example;
- a completed readiness checklist and confidence reflection.

This review has **no flag**. Your evidence is your answers and explanations.

## Key Takeaways

- Preflight first: target, status, terminal, notes.
- A command has an executable, options, and arguments.
- Permissions control who can read, write, and execute.
- A process is not a service; a listener is not a vulnerability.
- An open port is not a compromise.
- A log line is evidence, not a conclusion.
- Confidence needs a reason.
- Redact credentials and personal information.
- Stop when the target, data, or action is unclear.

If a skill is not ready, return to the linked page. That is what the review is
for.
