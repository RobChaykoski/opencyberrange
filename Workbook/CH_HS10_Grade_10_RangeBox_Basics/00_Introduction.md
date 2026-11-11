# Beginner Cybersecurity — Stage 2: Command Line, Files, and Networks

## Welcome

You are in **Beginner Stage 2**. Stage 1 taught you how to open RangeBox and use
the terminal safely. This stage moves you from following a list of commands to
explaining what you see and choosing the next safe step.

You will build confidence with:

- command-line fluency;
- files, permissions, and paths;
- processes and services;
- network connections and ports;
- one bounded service observation;
- logs and evidence notes;
- a guided beginner challenge.

You do not need to install anything. Every target is fictional and isolated.

## Where You Work

| Place | What it is | What you use it for |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Reading the workbook and keeping notes. |
| **Web browser** | The app that shows the OpenCyberRange page. | Opening the exercise and the RangeBox viewer. |
| **Exercise panel** | The part of the exercise page with the lab status, targets, and controls. | Finding the assigned target and starting or stopping the lab. |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Your practice workstation. |
| **RangeBox terminal** | The text window inside RangeBox. | Running the commands in this stage. |
| **Assigned target** | The practice server named in the current exercise. | **The only network system you may contact in that exercise.** |

Only the target shown in the exercise panel is in scope. A target being reachable
does not make it authorized.

## RangeBox Interface Refresher

These are the controls you will see. Use the labels, not colours or positions.

| Control | What it does | Does it stop the lab? |
|---|---|---|
| **Start Exercise** | Starts the lab from the exercise panel. | Starts it. |
| **Launch RangeBox** | Starts the standalone RangeBox desktop. | Starts the desktop. |
| **Open RangeBox** | Opens the RangeBox viewer for a running exercise. | No. |
| **Reconnect** | Tries to restore a lost viewer connection. | No. |
| **Clipboard** | Opens the text clipboard panel in the RangeBox viewer. | No. |
| **Minimize** / **Expand** | Hides or restores the RangeBox viewer. | No. |
| **Fullscreen** / **Exit FS** | Expands the viewer or returns it to normal size. | No. |
| **Close RangeBox** | Closes the standalone RangeBox viewer when that control is shown. | Not necessarily. |
| **Stop Exercise** | Ends the exercise lab. | **Yes.** Unsaved work may be lost. |
| **Stop RangeBox** | Stops the standalone RangeBox desktop. | **Yes.** Unsaved work may be lost. |
| **Exit** | Leaves the exercise panel. | No. The lab keeps running. |
| **Logout** | Ends your OpenCyberRange login session. | Not automatically. Stop the lab first. |

If the viewer is blank or unresponsive, try **Reconnect**, **Open RangeBox**, or
**Expand** before you stop the lab. Save notes before any reset.

## Stage 1 Skills Check

You are ready for Stage 2 when you can do the following. If you mark **Not yet**
or **Almost**, revisit the linked page before continuing.

| I can… | Practice page |
|---|---|
| Open RangeBox and find the terminal. | [Signing In and Opening RangeBox](../CH_HS09_Grade_9_RangeBox_Basics/01_First_Steps.md) |
| Run `pwd`, `whoami`, and `ls` and explain the output. | [Terminal Foundations](../CH_HS09_Grade_9_RangeBox_Basics/03_Terminal_Foundations.md) |
| Explain absolute and relative paths and case sensitivity. | [Files, Folders, and Paths](../CH_HS09_Grade_9_RangeBox_Basics/04_Files_Folders_and_Paths.md) |
| Explain host, client, server, IP address, hostname, service, and port. | [Internet and Network Basics](../CH_HS09_Grade_9_RangeBox_Basics/05_Internet_and_Network_Basics.md) |
| Find the assigned target and stop on a mismatch. | [Target and Connectivity Check](../CH_HS09_Grade_9_RangeBox_Basics/06_Target_and_Connectivity_Check.md) |
| Explain authorization and privacy, and describe a concern without sharing sensitive data. | [Cyber Ethics, Privacy, and Digital Citizenship](../CH_HS09_Grade_9_RangeBox_Basics/08_Cyber_Ethics_Privacy_and_Digital_Citizenship.md) |
| Choose a safe recovery step and leave the lab cleanly. | [RangeBox Troubleshooting and Safe Exit](../CH_HS09_Grade_9_RangeBox_Basics/09_RangeBox_Troubleshooting_and_Safe_Exit.md) |

### Readiness check

This is not graded. Mark one box for each statement.

| I can… | Not yet | Almost | Yes |
|---|---|---|---|
| Open RangeBox and find the terminal. | [ ] | [ ] | [ ] |
| Run a command and read the output. | [ ] | [ ] | [ ] |
| Find my current folder with `pwd`. | [ ] | [ ] | [ ] |
| Explain why Linux paths are case-sensitive. | [ ] | [ ] | [ ] |
| Explain what a hostname, IP address, port, and service are. | [ ] | [ ] | [ ] |
| Find the assigned target and stop when it does not match. | [ ] | [ ] | [ ] |
| Explain what authorization means. | [ ] | [ ] | [ ] |
| Keep notes outside RangeBox. | [ ] | [ ] | [ ] |
| Stop the lab and log out on a shared device. | [ ] | [ ] | [ ] |

If you are new to the beginner track, start with **Beginner Stage 1**. You can
return to this stage when the checks above feel comfortable.

## Words to Review

These words were introduced in Stage 1. Read them again before you continue.

| Term | What it means |
|---|---|
| **RangeBox** | The remote Linux desktop provided by the platform and shown in your browser. |
| **Terminal** | The text window inside RangeBox where you type commands. |
| **Command** | An instruction typed into the terminal. |
| **Path** | The route to a file or folder, written with `/` between folder names. |
| **Current directory** | The folder you are working in now. `pwd` prints it. |
| **IP address** | A number-based address of a host on a network. |
| **Hostname** | A human-readable name that maps to an IP address, such as `network.lab`. |
| **Service** | A program on a server that provides something, such as a web page. |
| **Port** | A number that identifies which service on a host should receive a request. |
| **Target** | The practice server assigned to the activity. It is the only system in scope. |
| **Authorization** | Permission for a specific action on a specific system. It is not the same as being able to do it. |
| **Evidence** | Information that shows what happened, such as command output or a log line. Collect the minimum needed. |

## What You Will Learn

By the end of this stage, you will be able to:

- complete a five-minute RangeBox preflight;
- use commands, options, arguments, pipes, and redirection with disposable data;
- explain file permissions and ownership;
- connect applications, processes, services, and ports;
- interpret a simple client-server connection;
- perform one bounded service observation and explain the result;
- read a small log and separate observation from interpretation;
- write reproducible evidence notes and a short finding;
- complete a guided beginner challenge within scope;
- troubleshoot, reset, and exit safely;
- explain a decision, not just report a flag.

## How Each Page Is Designed

Every page in this stage follows the same beginner pattern:

- **Where and what:** the place, the tool, and the assigned target;
- **Words first:** new terms are defined before they are used;
- **Predict, act, verify:** you write what you expect, run one action, and check
  the result;
- **Recovery:** a safe path for a likely mistake;
- **Evidence:** a note, table, or explanation you can show;
- **Next safe step:** what to do after success, and when to stop and ask.

All Stage 2 labs are marked **beginner**. The stage is designed for learners who
have completed Stage 1 or who can pass the readiness check above. It does not
assume prior cybersecurity experience.

## Estimated Time

Plan for about **4–6 hours across the stage**. Each page is about **15–30
minutes**, and the applied labs are about **20–30 minutes** each. This is a
planning estimate, not a deadline. You can split the work across sessions.

## What You Need

- [ ] A laptop or desktop with a browser. A tablet with a keyboard may work; a
      phone is not recommended for terminal work.
- [ ] Your OpenCyberRange account. Do not share your password.
- [ ] The exercise panel open in the **Beginner Cybersecurity** track.
- [ ] RangeBox, or the lab browser or terminal your teacher provides as a
      fallback.
- [ ] A notes file outside RangeBox for commands, evidence, and reflections.

## How to Ask for Help

1. Read the step again and check for a typo.
2. Open the activity's **Hint**.
3. Write three things: the step, what you expected, and what happened.
4. Ask your teacher. Do not share your password or screenshot a password field.
5. If you feel stuck or unsafe, stop. You can return later.

Errors are information. They tell you that a command, a path, or a connection did
not work as expected.

## How to Reset

Use the least disruptive step first.

1. Save your notes outside RangeBox.
2. If the viewer is blank or disconnected, use **Reconnect** or **Open RangeBox**.
3. If one application is unresponsive, close only that application window.
4. If the lab must be reset, use **Stop Exercise** or **Stop RangeBox**.
5. Wait for the status to show that it stopped.
6. Use **Start Exercise** or **Launch RangeBox** to begin again.
7. Recheck the target in the exercise panel; a fresh lab may have a new IP
   address.

Do not disable browser security, antivirus, firewall, or school protections as a
generic fix. Ask your teacher.

## Accessibility Options

- **Zoom:** use browser zoom, or `Ctrl` + `+` / `Ctrl` + `-`
  (`Cmd` + `+` / `Cmd` + `-` on a Mac).
- **Keyboard:** use `Tab` and `Shift` + `Tab` to move between controls, and
  `Enter` or `Space` to activate them.
- **Reduced motion:** turn on your device's reduced-motion setting if animation
  bothers you.
- **Clipboard:** use the **Clipboard** button in RangeBox to move text between the
  browser and the desktop.
- **Text labels:** instructions use labels and positions, not colours alone.
- **Breaks and time:** take breaks and ask your teacher about extra time.
- **Assistive tools:** tell your teacher what you need. Ask if a label or
  instruction is unclear.

## What You May Do

- Start the exercise and use RangeBox.
- Run the commands shown in the activities.
- Use hints whenever you are stuck.
- Ask your teacher or classmates for help with the task.
- Take breaks.
- Stop and relaunch the lab if you need a fresh start.

## What to Avoid

- Use only the target shown in your exercise. Do not contact your own device,
  your school network, another student's lab, or the public internet.
- Do not scan public or adjacent addresses, or try ports that the activity does
  not list.
- Do not use `sudo`, broad wildcards, `rm -r`, or `rm -rf`.
- Do not share your account, password, tokens, or screenshots containing
  credentials.
- Do not enter real personal information or investigate classmates.
- If you are unsure whether something is allowed, stop and ask.

## Success Evidence

You are ready to move on when you can show:

- a completed preflight check;
- command output with a short explanation of what each command did;
- one permission and one process/service observation;
- one network or service observation with the target and port identified;
- one log interpretation that separates observation from conclusion;
- one evidence note with timestamp, target, action, result, meaning, and next
  step;
- one guided-challenge conclusion with a confidence level;
- a cleanup check showing notes saved, files handled, and the session closed;
- the correct flag for each lab that has one.

A flag shows that you reached the end. Your notes and explanation show that you
understand what you did.

## Activities

1. [RangeBox Review and Preflight](01_RangeBox_Review_and_Preflight.md) — confirm
   the workspace, identity, files, network, and target before you act.
2. [Command Line Fluency](02_Command_Line_Fluency.md) — build confidence with
   commands, options, arguments, pipes, redirection, and output.
3. [Files, Permissions, and Ownership](03_Files_Permissions_and_Ownership.md) —
   understand who can read, change, and run files.
4. [Processes, Services, and Applications](04_Processes_Services_and_Applications.md)
   — connect running programs to network services.
5. [Network Communication and Ports](05_Network_Communication_and_Ports.md) —
   explain client-server connections and connection states.
6. [Introductory Service Enumeration](06_Introductory_Service_Enumeration.md) —
   observe one assigned service safely and record the evidence.
7. [Logs and Event Review](07_Logs_and_Event_Review.md) — read basic system and
   application events.
8. [Evidence Notes and Technical Communication](08_Evidence_Notes_and_Technical_Communication.md)
   — record reproducible steps and explain findings clearly.
9. [Guided Cybersecurity Challenge](09_Guided_Cybersecurity_Challenge.md) — apply
   the stage skills in a bounded beginner scenario.
10. [Troubleshooting, Reset, and Safe Exit](10_Troubleshooting_Reset_and_Safe_Exit.md)
    — recover independently and leave the lab clean.
11. [Chapter Review](11_Chapter_Review.md) — check your skills, reflect, and
    decide what to practise next.

## Applied Labs

These existing labs give you extra practice with the stage skills. Use the target
shown in each exercise.

- [RangeBox Network Basics](01_Network_Basics.md) — read a status code and
  response headers.
- [RangeBox Browser and Source](02_Browser_and_Source.md) — inspect the HTML a
  browser receives.
- [Dissect an Email](03_Email_Metadata.md) — read raw email headers.
- [MFA and the Lost Phone](04_MFA_Lost_Phone.md) — trace an account recovery
  path.

Start with [RangeBox Review and Preflight](01_RangeBox_Review_and_Preflight.md).
Take it one check at a time, and ask for help when you need it.
