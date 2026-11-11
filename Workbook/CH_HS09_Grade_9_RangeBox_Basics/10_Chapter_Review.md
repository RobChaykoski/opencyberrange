# Chapter Review

This is the final review for the **Stage 1: RangeBox Foundations** chapter. It is a
**readiness gate**, not a speed test and not a grade. It checks whether you can
work safely, explain your choices, and recover from common problems.

You do not need to memorise commands. You need to know what to use, where to use
it, and when to stop.

## Before You Begin

### Where to run this review

| Place | What it is | Used in this review? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, to read the page and write your answers. |
| **Notes file** | Your own notes, outside RangeBox. | **Yes. Write your answers here.** |
| **Web browser** | The app that shows this page and the exercise. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | Only if you choose to try a command from the reference. |
| **Assigned target** | A practice server named in an exercise. | **This review does not assign a target.** If a question mentions one, use only the target shown in the current exercise. |
| **Public internet** | Real websites and services. | **No.** |

This review has **no commands you must run** and **no flag**. The one-page
reference near the end is for your notes and later practice.

### How this review works

- **Matching:** connect a term to its meaning.
- **Sequencing:** put steps in a safe order.
- **Screenshot interpretation:** read a text description of a screen and identify
  the local browser, the remote desktop, the prompt, and the output.
- **Scenario:** read a short situation and choose a safe action.
- **Remediation:** the activity to revisit if a skill is not ready yet.
- **Readiness gate:** a checklist you complete when you can explain the skills,
  not a score.

There are no trick questions. If a question seems unclear, write what you would
check or who you would ask.

### The commands in the reference

The reference uses commands you already met. Where a command has a replaceable
value, it is written in capitals, such as `FILE` or `FOLDER`. Replace it with the
real name from your activity. Do not type the capital word itself.

### What this review checks

- workspace recognition;
- terminal basics;
- paths and case sensitivity;
- networking vocabulary;
- target verification;
- authorization and privacy;
- troubleshooting and cleanup;
- your ability to explain a safe decision.

## Part 1: Matching

Match each term in the left column with one meaning in the right column. Write
the letter next to the number.

| # | Term | Letter | Meaning |
|---|---|---|---|
| 1 | Hostname | | A. Permission for a specific action on a specific system. |
| 2 | Port | | B. A secret that proves identity and allows access. |
| 3 | Client | | C. A name that maps to an IP address. |
| 4 | Server | | D. A path that starts at `/` and works from any folder. |
| 5 | Absolute path | | E. A device or program that asks for data or a service. |
| 6 | Relative path | | F. Reporting a problem privately so it can be fixed. |
| 7 | Authorization | | G. A number that identifies a service on a host. |
| 8 | Consent | | H. A path that starts from the current directory. |
| 9 | Credential | | I. A device or program that provides data or a service. |
| 10 | Responsible disclosure | | J. A clear agreement for information or actions that can be withdrawn. |

## Part 2: Sequencing

### A. Safe exit

Put these actions in the safest order. Write 1 for the first action, 2 for the
second, and so on.

| Order | Action |
|---|---|
| | Close the RangeBox viewer and extra browser tabs. |
| | Save your notes outside RangeBox. |
| | Logout on a shared device. |
| | Stop the lab with **Stop Exercise** or **Stop RangeBox**. |

### B. Recovering from a command error

Put these steps in order.

| Order | Action |
|---|---|
| | Run the command again once. |
| | Read the error message. |
| | Check `pwd` and `ls`. |
| | Fix the spelling, case, or spaces. |
| | Ask your teacher if it still fails. |

## Part 3: Text Description of a Screenshot

This is a text description, not a real screenshot. It contains no personal data.
Read it and answer the questions.

```text
Browser frame
  Address bar: the OpenCyberRange address from your teacher
  One browser tab: OpenCyberRange

RangeBox viewer
  Toolbar (may show): Clipboard | Minimize or Expand | Fullscreen | Reconnect | Close
  Remote desktop window: Terminal

Terminal contents
  $ pwd
  /home/kali
```

1. Which part is running on your student device: the browser frame or the
   RangeBox desktop?
2. Which part is remote: the browser frame or the RangeBox desktop?
3. Which text is the prompt?
4. Which text is the output of `pwd`?
5. What does `/home/kali` mean?
6. Which control would you use to make the viewer larger?
7. If the terminal showed `C:\Users\...` instead, what would that tell you?

## Part 4: Short Scenarios

For each scenario, write what you would do first, who you would tell, and what
you would **not** copy or share. There can be more than one safe answer.

### Scenario 1: Target mismatch

The exercise panel shows `rangebox.lab` on port `9090`. The workbook example says
`rangebox.lab` on port `8080`. Your Target Card has `8080`.

### Scenario 2: Shared account

You open a shared classroom laptop and the previous student's messages are still
on the screen.

### Scenario 3: Screenshot in a group chat

A group chat contains a screenshot of a classmate's private message. Someone asks
you to forward it.

### Scenario 4: Command error

You run `cat notes.txt` and see:

```text
cat: notes.txt: No such file or directory
```

### Scenario 5: Unsaved notes

You wrote notes inside the RangeBox desktop. The viewer disconnects before you
copy them out.

### Scenario 6: Cleanup

You downloaded `welcome.txt` into `~/practice-files`. You want to remove it before
you leave.

### Scenario 7: Authorization

You can reach another student's lab target from your RangeBox terminal. It is not
the target in your exercise.

### Scenario 8: Possible website exposure

You notice a school website page that seems to list files that should not be
public.

## Part 5: One-Page Beginner Reference

Keep this section in your notes.

### Safe commands

| I need to… | Command | Replace this |
|---|---|---|
| Find my current folder | `pwd` | Nothing. |
| Find my RangeBox account | `whoami` | Nothing. |
| List the current folder | `ls` | Nothing. |
| Create a folder | `mkdir -p FOLDER` | `FOLDER` with a real folder name. |
| Enter a folder | `cd FOLDER` | `FOLDER` with a real folder name. |
| Read a text file | `cat FILE` | `FILE` with a real file name. |
| Copy a file | `cp SOURCE DEST` | `SOURCE` and `DEST` with real names. |
| Move or rename a file | `mv SOURCE DEST` | `SOURCE` and `DEST` with real names. |
| Remove one file | `rm FILE` | `FILE` with the exact name. |
| Remove one empty folder | `rmdir FOLDER` | `FOLDER` with the exact name. |
| Check one service | `curl -I http://TARGET:PORT/PATH` | `TARGET`, `PORT`, and `PATH` from the exercise. |
| Cancel a command line | `Ctrl` + `C` | Nothing. |
| Switch windows | `Alt` + `Tab` | Nothing. |
| Close one application window | `Alt` + `F4` | Nothing. |

**Never** use `sudo`, `rm *`, `rm -r`, or `rm -rf`. Run commands only in the
RangeBox terminal, not on your student device.

The option `-p` in `mkdir -p` means "create the folder if it is missing, and do
not treat an existing folder as an error". The option `-I` (capital letter I) in
`curl -I` means "send a HEAD request and show response headers only". `rm` and
`rmdir` have no undo. Before `cp` or `mv`, run `ls` and check the destination;
`mv` can replace an existing file.

### Key terms

| Term | One-line meaning |
|---|---|
| Host | A device on a network with an address. |
| Client | A device or program that asks for data or a service. |
| Server | A device or program that provides data or a service. |
| IP address | A number-based address of a host. |
| Hostname | A name that maps to an IP address. |
| Port | A number that identifies a service on a host. |
| Service | A program that provides something, such as a web page. |
| Protocol | Agreed rules for communication. |
| Request | A message a client sends. |
| Response | A message a server sends back. |
| Authorization | Permission for a specific action on a specific system. |
| Consent | A clear agreement that can be withdrawn. |
| Privacy | A person's control over who can see and use their information. |
| Credential | A secret that proves identity and allows access. |
| Evidence | Information that shows what happened. Collect the minimum needed. |
| Responsible disclosure | Reporting a problem privately so it can be fixed. |
| Digital citizenship | Using technology safely, respectfully, legally, and with care. |

### Help steps

1. Read the step again and check for a typo.
2. Open the activity's **Hint**.
3. Write three things: the step, what you expected, and what happened.
4. Ask your teacher. Do not share your password.
5. If you feel stuck or unsafe, stop. You can return later.

### Stop conditions

Stop and ask a trusted adult if:

- the target in the exercise panel does not match your Target Card;
- you see another student's messages, files, or personal information;
- a password, token, or other credential may have been exposed;
- a browser security warning appears;
- you are asked to contact a system outside the exercise;
- you are unsure whether an action is allowed;
- you are unsure whether a file is safe to open or delete.

## Part 6: Confidence Reflection

This is not graded. Mark one box for each statement.

| I can… | Not yet | Almost | Yes |
|---|---|---|---|
| Find RangeBox, the desktop, and the terminal. | [ ] | [ ] | [ ] |
| Run `pwd`, `whoami`, and `ls` and explain the output. | [ ] | [ ] | [ ] |
| Tell an absolute path from a relative path. | [ ] | [ ] | [ ] |
| Explain why Linux paths and file names are case-sensitive. | [ ] | [ ] | [ ] |
| Explain host, client, server, IP address, hostname, protocol, service, port, request, and response. | [ ] | [ ] | [ ] |
| Find the assigned target and stop when it does not match. | [ ] | [ ] | [ ] |
| Explain authorization, consent, and privacy. | [ ] | [ ] | [ ] |
| Protect credentials and personal information. | [ ] | [ ] | [ ] |
| Describe a concern without exposing sensitive data. | [ ] | [ ] | [ ] |
| Choose a least-disruptive recovery step. | [ ] | [ ] | [ ] |
| Clean up files, credentials, and open sessions. | [ ] | [ ] | [ ] |
| Ask for help without sharing my password. | [ ] | [ ] | [ ] |

If you mark **Not yet** or **Almost**, that is useful information. Revisit the
linked activity before you move on.

## Part 7: Readiness Checklist

- [ ] I completed the matching, sequencing, screenshot, and scenario sections.
- [ ] I can explain my answers in my own words.
- [ ] I know where the target appears and what to do on a mismatch.
- [ ] I know the stop-and-report process.
- [ ] I know how to save notes outside RangeBox.
- [ ] I know how to stop the lab and logout on a shared device.
- [ ] I know which activity to revisit for each skill.
- [ ] I have not shared a password or real personal information.

## If You Are Unsure

- If you cannot answer a question, mark it and revisit the linked activity.
- If two answers seem safe, choose the one that stops and asks before acting.
- If a question mentions a target that is missing or different, stop. Do not
  guess or try another target.
- If you are unsure whether a detail is personal information, leave it out.
- A wrong answer is information. It shows which activity to practise again, not
  a failure.

## Remediation Pointers

Use the exact activity for the skill you want to practise again.

| Skill | Activity to revisit |
|---|---|
| Workspace, sign-in, and finding the terminal | [Signing In and Opening RangeBox](01_First_Steps.md) |
| Browser and RangeBox controls, windows | [RangeBox Desktop and Window Basics](02_RangeBox_Desktop_and_Window_Basics.md) |
| Terminal, prompt, command, option, argument, output | [Terminal Foundations](03_Terminal_Foundations.md) |
| Files, folders, paths, case sensitivity | [Files, Folders, and Paths](04_Files_Folders_and_Paths.md) |
| Network vocabulary, requests, ports | [Internet and Network Basics](05_Internet_and_Network_Basics.md) |
| Target verification and connectivity check | [Target and Connectivity Check](06_Target_and_Connectivity_Check.md) |
| Combining identity, location, note, target, and check | [Basic Command Practice](07_Basic_Command_Practice.md) |
| Authorization, privacy, reporting | [Cyber Ethics, Privacy, and Digital Citizenship](08_Cyber_Ethics_Privacy_and_Digital_Citizenship.md) |
| Recovery, safe exit, cleanup | [RangeBox Troubleshooting and Safe Exit](09_RangeBox_Troubleshooting_and_Safe_Exit.md) |
| Reading a link safely | [Read the Link Before You Click](06_Read_The_Link.md) |
| Checking a file safely | [Know the File Before You Open It](07_Know_The_File.md) |
| Combining digital-safety habits | [Capstone: The Forwarded Message](08_Forwarded_Message.md) |

## Answers and Explanations

Cover this section until you have finished Parts 1–4. Many scenario answers are
safe if they stop, protect, tell, and avoid exposing data.

### Part 1: Matching

1-C, 2-G, 3-E, 4-I, 5-D, 6-H, 7-A, 8-J, 9-B, 10-F.

- A hostname is a name that maps to an IP address.
- A port is a number that identifies a service on a host.
- A client asks; a server provides.
- An absolute path starts at `/`; a relative path starts from the current folder.
- Authorization is permission, not ability.
- Consent is a clear agreement that can be withdrawn.
- A credential is a secret that allows access.
- Responsible disclosure reports a problem privately so it can be fixed.

### Part 2: Sequencing

**A. Safe exit:** 1 — Save your notes outside RangeBox. 2 — Stop the lab with
**Stop Exercise** or **Stop RangeBox**. 3 — Close the RangeBox viewer and extra
browser tabs. 4 — Logout on a shared device.

**B. Command error:** 1 — Read the error message. 2 — Check `pwd` and `ls`.
3 — Fix the spelling, case, or spaces. 4 — Run the command again once. 5 — Ask
your teacher if it still fails.

### Part 3: Screenshot description

1. The browser frame is on the student device.
2. The RangeBox desktop is remote.
3. The prompt is `$`.
4. The output is `/home/kali`.
5. It is the home folder of the practice account.
6. Use **Fullscreen**, or **Expand** if the viewer is minimized.
7. You are in a terminal on a Windows device, not in the RangeBox terminal.
   Return to RangeBox and do not run commands there.

### Part 4: Scenario guidance

1. **Target mismatch:** stop. Do not run the check. Write down both targets and
   ask your teacher. Do not try port 9090 or 8080 to see which works.
2. **Shared account:** do not read or copy the messages. Leave the device as it
   is and tell the teacher, who can secure it.
3. **Screenshot in a group chat:** do not forward it. Tell a trusted adult. If an
   adult needs evidence, share it only through the approved channel.
4. **Command error:** read the error. Run `pwd` and `ls`. Check the spelling,
   case, and folder. Fix the command and try once. Ask if it still fails.
5. **Unsaved notes:** do not reset first. Try **Reconnect** or **Open RangeBox**.
   If the notes are visible, copy them to your notes file. If they are lost, tell
   your teacher and reconstruct what you can. Keep notes outside next time.
6. **Cleanup:** run `pwd` and confirm you are in `~/practice-files`. Run `ls` and
   identify `welcome.txt`. Run `rm welcome.txt`. Run `ls` again. Do not use a
   wildcard or `rm -r`.
7. **Authorization:** do not use it. It is not your assigned target. Stop and ask
   your teacher if you are unsure. A reachable target is not authorization.
8. **Possible website exposure:** stop. Do not open the files, test the page, or
   share the link. Tell your teacher or school IT staff. Describe what you saw
   without collecting data.

## What Success Looks Like

You are ready to finish when you can show:

- completed matching, sequencing, screenshot, and scenario answers;
- one explanation of a target mismatch and the stop rule;
- one explanation of how to protect a credential or personal information;
- one explanation of the difference between closing the tab and stopping the lab;
- a completed readiness checklist;
- a confidence reflection with at least one next step if you marked **Not yet**
  or **Almost**.

This review has **no flag**. Your evidence is your answers and your explanations.

## Key Takeaways

- Safety comes before speed. Stop when the target, authorization, or privacy is
  unclear.
- Explain what a command does, not just what you typed.
- A hostname is a name; a port identifies a service; a client asks and a server
  responds.
- Absolute paths start at `/`; relative paths start from the current folder.
- Linux paths and file names are case-sensitive.
- Authorization is permission, not ability. Consent can be withdrawn.
- Protect credentials and personal information. Report privately.
- Recover with the least disruptive step. Save notes before a reset.
- Closing a tab is not stopping the lab. **Stop Exercise** or **Stop RangeBox**
  ends the lab.
- Clean up files, credentials, personal information, and open sessions before you
  leave.

If a skill is not ready yet, return to the linked activity. That is what the
review is for.
