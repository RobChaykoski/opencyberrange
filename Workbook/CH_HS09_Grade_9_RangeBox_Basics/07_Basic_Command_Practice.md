# Basic Command Practice

This extra practice activity combines the skills from the earlier pages:

- checking your **identity**;
- confirming your **location**;
- creating a **workspace folder**;
- creating a **note** and recording the assigned target;
- performing **one safe connectivity check**.

You will not scan, log in, exploit, or download a new tool. Each step is
independent, so if one step fails you can fix that step and continue without
restarting the whole environment.

## Before You Begin

Complete [Terminal Foundations](03_Terminal_Foundations.md),
[Files, Folders, and Paths](04_Files_Folders_and_Paths.md), and
[Target and Connectivity Check](06_Target_and_Connectivity_Check.md) first.

### Where to run this activity

| Place | What it is | Used in this activity? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, for your notes file and the browser. |
| **Web browser** | The app that shows the exercise page and the RangeBox desktop. | Yes. |
| **Exercise panel** | The part of the exercise page that shows the lab status and targets. | **Yes. This is where you find the assigned target.** |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Yes. This is your practice workstation. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run the commands here.** |
| **Assigned target** | The practice server named in your exercise. | **Yes. This is the only network system you may contact.** |
| **Public internet** | Real websites and services outside the lab. | **No. It is out of scope.** |

The workbook example for this chapter is `rangebox.lab:8080`. The exercise panel
is the source of truth for your lab.

!!! warning "Stop if the target does not match"
    If the exercise panel shows a different hostname or port from
    `rangebox.lab:8080`, do not run the connectivity check. Write down both
    values, stop, and ask your teacher. Do not guess, try both, or scan.

### What you need

- [ ] The RangeBox terminal open.
- [ ] The exercise panel open, with the exercise running.
- [ ] Your notes file, with a new section called **Target Card**.
- [ ] About **15–20 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain why you check your identity and location before acting;
- create and remove a small workspace folder safely;
- record the assigned target in a note before using it;
- run one read-only connectivity check;
- explain the result in your own words;
- reset only this activity without deleting unknown files or restarting the
  whole environment.

## Words to Know

| Term | What it means |
|---|---|
| **Identity** | The account you are using inside RangeBox. `whoami` prints it. |
| **Location** | The folder you are working in now. `pwd` prints it. |
| **Workspace folder** | A small folder for one activity. In this activity it is `command-practice`. |
| **Note** | A written record in your notes file. It survives a lab reset. |
| **Target Card** | The labelled note that records the target label, hostname, port, path, and where you found them. |
| **Connectivity check** | One read-only request to one known host, port, and path to see whether the service answers. |
| **Reset** | Return this activity to a known starting point without deleting unknown files or stopping the whole lab. |

## The Sequence at a Glance

| Step | Action | Why |
|---|---|---|
| 1 | Check identity with `whoami` | Know which account is acting. |
| 2 | Confirm location with `pwd` | Avoid creating a folder in the wrong place. |
| 3 | Create `command-practice` | Keep this activity separate from other work. |
| 4 | Enter `command-practice` | Put all file actions in one known folder. |
| 5 | Create the Target Card note | Record the target before using it. |
| 6 | Record the assigned target | Make the allowed target visible and check it. |
| 7 | Run one connectivity check | Confirm the target service answers. |
| 8 | Record the result | Turn the output into evidence you can explain. |
| 9 | Reset only this activity | Leave a clean state without deleting unknown files. |

## Walkthrough

Each step has a checkbox. Tick it only after you see the expected result.

### Step 1: Check your identity

- [ ] Run:

```bash
whoami
```

**Why:** you should know which RangeBox account is running the commands. This is
not your OpenCyberRange login.

**Expected result:** one short line with the practice account name, such as
`kali`. Your practice account may be different. Write the name in your Target
Card.

**If you see something different:** write down what you see. Do not guess. Ask
your teacher if the account name is unclear.

### Step 2: Confirm your location

- [ ] Run:

```bash
pwd
```

**Why:** a file action creates or changes something in the current folder. You
need to know where that is before you act.

**Expected result:** `/home/kali`, or another path that your teacher confirms is
your home folder.

**If you see a different path:** stop and ask before creating anything. Do not
run `mkdir` in an unknown folder.

### Step 3: Create the workspace folder

- [ ] Run:

```bash
mkdir -p command-practice
```

**Why:** a separate workspace keeps this activity away from your other files. The
option `-p` means "create the folder if it is missing, and do not treat an
existing folder as an error". This activity creates only the folder, because the
Target Card belongs in your persistent notes file. Later labs will put files
here.

**Expected result:** the command finishes without an error.

- [ ] Verify with:

```bash
ls
```

**Expected result:** `command-practice` appears in the list.

**If you see `File exists`:** the folder is already there. That is fine. Continue
to Step 4.

### Step 4: Enter the workspace

- [ ] Run:

```bash
cd command-practice
pwd
```

**Why:** now every file action in this activity happens in one known folder.

**Expected result:** `/home/kali/command-practice`.

**If `cd` says `No such file or directory`:** run `pwd` and `ls`. Go back to Step
3 and create the folder again. Check the spelling and case.

### Step 5: Create the Target Card note

- [ ] Open your notes file and start a new section called **Target Card**.

- [ ] Copy this template into the note:

```text
Target Card — Basic Command Practice

Activity:
Date:
RangeBox account:
Current folder:
Target label:
Hostname:
Port:
Path:
Where I found the target:
Workbook example: rangebox.lab:8080
Do the hostname and port match? Yes / No
If No, I stopped and asked: Yes / No
```

**Why:** a note outside RangeBox survives a lab reset. It also makes you write
down the allowed target before you use it.

**Expected result:** your note has a **Target Card** section with the activity,
date, account, and current folder filled in.

**If you do not have a notes file:** ask your teacher where to keep notes. Do not
store the only copy inside the temporary RangeBox desktop.

### Step 6: Record the assigned target

- [ ] Open the exercise panel and find the **Targets** section.

- [ ] Copy the **target label**, **hostname**, **IP address**, and **port** into
  the Target Card.

- [ ] Write the **path** `/welcome.txt` in the Target Card.

**Why:** the exercise panel is the source of truth. Recording the target makes a
mismatch visible before you run a network command.

**Expected result:** the Target Card shows the same hostname and port as the
workbook example, `rangebox.lab:8080`.

Do not use an IP address from another student, a screenshot, or a website. The
IP address may change when the lab starts; the hostname and port are the values
to compare.

**If the hostname or port is different:** stop. Do not run Step 7. Write down both
values and ask your teacher.

**If you do not see a target:** stop and ask. Do not scan the network to discover
one.

### Step 7: Run one connectivity check

- [ ] In the RangeBox terminal, run:

```bash
curl -I http://rangebox.lab:8080/welcome.txt
```

**Why:** this confirms that RangeBox can reach the one assigned service. It is a
read-only check. It asks for response headers only and does not download the file
body.

**Expected result:** a response that starts with an HTTP status line, followed by
headers. A line such as `HTTP/1.1 200 OK` means success.

The option `-I` is a capital letter I. It sends a **HEAD** request. It does not
save a file, log in, or change the target.

**If your teacher confirmed a different target:** use only the exact values from
the Target Card:

```text
curl -I http://TARGET:PORT/PATH
```

Replace `TARGET`, `PORT`, and `PATH` with the values you wrote down. Do not guess
or try other values.

### Step 8: Record the result

- [ ] Copy the status line or error message into your Target Card.

- [ ] Write one sentence explaining what happened.

**Why:** the command output is not the whole evidence. You need to explain what
it means.

**Expected result:** your note contains one of these kinds of sentences:

- "The target answered with `200 OK`, so RangeBox can reach the service on port
  8080."
- "The hostname did not resolve, so I stopped and checked the exercise instead of
  trying another address."
- "The connection was refused, so I checked that the lab was running before
  trying again."

**If the status is not `200`:** the connection still worked. Check the path or ask
your teacher. Do not scan.

**If there is no response:** wait about 10 seconds, then press `Ctrl` + `C`.
Record "timeout" and check the lab status. Do not try another host or port.

### Step 9: Reset only this activity

- [ ] Run:

```bash
cd ~
pwd
```

**Why:** return to your home folder without stopping the lab.

**Expected result:** `/home/kali`.

- [ ] Check whether the workspace is empty:

```bash
ls command-practice
```

**Expected result:** no files are listed.

- [ ] If the folder is empty, remove it:

```bash
rmdir command-practice
```

**Why:** this removes only the empty folder you created. It does not touch your
Target Card, your notes, or any unknown file.

**Expected result:** `rmdir` finishes without an error. `ls` no longer shows
`command-practice`.

**If the folder is not empty:** stop. Do not delete files you do not recognise.
Leave the folder in place and ask your teacher. You can still finish the
activity; the extra folder is not a failure.

## Reset Paths

Use the smallest reset that fixes the problem. You do not need to restart the
whole environment for a wrong note, a wrong folder, or a failed check.

| Problem | Smallest safe reset |
|---|---|
| Wrong note entry | Start a new Target Card section. Keep the old one as evidence. |
| Wrong folder | Run `cd ~/command-practice` or `cd ~`. Check with `pwd`. |
| Workspace folder missing | Run `mkdir -p command-practice` again. |
| Workspace folder not empty | Do not delete unknown files. Leave it and ask your teacher. |
| Connectivity check failed | Read the error, check the target and lab status, then try the same check once more. Do not try other hosts or ports. |
| The command hangs | Press `Ctrl` + `C` to cancel. You do not need to restart. |
| The target is wrong | Stop. Do not run the check. Write both values down and ask. |
| RangeBox is not responding | Use **Stop Exercise** only as a last resort, then launch the exercise again. Your notes outside RangeBox are safe. |

**Do not** solve a problem by deleting a folder you did not create, using a
wildcard, or restarting the whole environment. Ask first.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Unknown account | `whoami` shows a name you did not expect | Write it down. Ask your teacher. Do not change account. |
| Unknown folder | `pwd` shows a path outside your home folder | Stop. Run `cd ~`, then `pwd`. |
| Folder already exists | `mkdir: cannot create directory ... File exists` | Continue to Step 4. This is not an error for this activity. |
| Folder missing | `cd: No such file or directory` | Run `pwd` and `ls`. Recreate the folder with `mkdir -p command-practice`. |
| Target missing | The exercise panel has no target | Stop and ask. Do not scan. |
| Target mismatch | The hostname or port differs from `rangebox.lab:8080` | Stop. Write both values down and ask. |
| Name resolution failure | `curl: (6) Could not resolve host` | Check the spelling and the exercise. Ask your teacher. |
| Connection refused | `curl: (7) ... Connection refused` | Check that the lab is running and the port matches the Target Card. |
| Timeout | No response, or a message containing `(28)` and `timed out` | Press `Ctrl` + `C` if needed. Check the lab status. |
| Status is not 200 | `403`, `404`, or `500` | The connection worked. Check the path or ask. Do not scan. |

## Explain Your Work

Answer these questions in your notes.

1. Which account did you use, and how did you check?
2. Which folder were you in before you created the workspace?
3. Why did you create `command-practice`?
4. Why did you put the Target Card outside RangeBox?
5. Where did you find the target in the exercise panel?
6. What hostname and port did you record?
7. Did they match the workbook example? If not, what did you do?
8. What did the connectivity check return?
9. What is one failure path, and what would you do?
10. What is the smallest reset for a wrong note entry?

## What Success Looks Like

You are ready to continue when you can show:

- the output of `whoami` and `pwd`;
- a `command-practice` folder that you created and checked;
- a completed Target Card with the target label, hostname, port, path, and
  source;
- the `curl -I` command and its output;
- one sentence explaining the result;
- one reset step that does not delete unknown files or restart the environment;
- a clear statement that the only network target was the assigned practice
  target.

This activity has **no flag**. Your evidence is your Target Card, your command
output, and your explanation.

## Key Takeaways

- Check identity and location before you act.
- A separate workspace keeps practice files easy to find and easy to reset.
- Write the target in a note before you use it. Compare the hostname and port
  with the exercise panel.
- One connectivity check uses one known host, port, and path, and it is
  read-only.
- A status code means the target answered. A connection error means it did not.
- Reset the smallest thing that is wrong. Do not delete unknown files or restart
  the whole environment.
- The command output is not the whole evidence. Your note and explanation show
  what you understand.

When you are ready, continue with [RangeBox File Hunt](02_File_Hunt.md).
