# RangeBox Review and Preflight

This is a **five-minute preflight**. You will confirm that you are in the right
browser tab, the right RangeBox session, the right terminal, the right folder,
and the right target before you run a network command.

A preflight is not a scan. It is a short set of checks that prevents a
scope mistake.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, for the browser and notes. |
| **Web browser** | The app that shows the OpenCyberRange page. | Yes. |
| **Exercise panel** | The page area with lab status, targets, and controls. | **Yes. This is where you confirm the target.** |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run the checks here.** |
| **Assigned target** | The practice server named in the current exercise. | **Yes. This is the only network system in scope.** |

This page uses the **RangeBox Network Basics** lab as its example. That lab's
target is `network.lab:8080`. If you are in a different lab, use the target named
on that lab's workbook page. If the exercise panel and the workbook page
disagree, **stop and ask**.

### What you need

- [ ] The exercise panel open in the **Beginner Cybersecurity** track.
- [ ] The lab running, or ready to start.
- [ ] Your notes file, with a **Target Card** section.
- [ ] About **5–10 minutes**.

### What you will be able to do

By the end of this preflight, you will be able to:

- tell the student device, browser, RangeBox desktop, and target apart;
- confirm your RangeBox identity and current folder;
- confirm that the expected lab files are visible;
- find and record the assigned target;
- stop and ask when the target does not match;
- recover from an expired session, missing file, wrong folder, disconnected
  viewer, or target mismatch.

## The Preflight

Tick each box only when you see the expected result.

### Step 1: Confirm the correct browser tab

- [ ] Look at your browser tabs. You should have **one OpenCyberRange tab** for
      your own account.

**Why:** a second tab may belong to another student or an older session.

**Expected result:** the OpenCyberRange exercise page is visible, and you know
which tab it is.

**If you are not sure:** close the extra tab. Do not sign in as another student.

### Step 2: Confirm the lab is running

- [ ] Look at the exercise panel status.

**Why:** commands fail when the lab is stopped or still starting.

**Expected result:** the status shows **Running**. If it shows **Starting**, wait.

- [ ] If the RangeBox viewer is not visible, choose **Open RangeBox**.

**If the lab is stopped:** choose **Start Exercise** and wait for **Running**.
If you use the standalone RangeBox page, choose **Launch RangeBox**.

**If the viewer is blank:** wait a moment, then try **Reconnect** or **Expand**.
Do not stop the lab yet.

### Step 3: Confirm the terminal prompt

- [ ] Open the terminal from the RangeBox panel or application menu.

**Why:** every command in this stage runs in the RangeBox terminal, not on your
student device.

**Expected result:** a terminal window with a prompt.

**If you see a Windows path such as `C:\Users\...` or a local PowerShell
prompt:** you are not in RangeBox. Return to the RangeBox desktop and open its
terminal.

### Step 4: Confirm your identity

- [ ] Run:

```bash
whoami
```

**Why:** you should know which RangeBox account is running the commands.

**Expected result:** one short line with the practice account name, such as
`kali`. Your account may be different.

**If the name is unexpected:** write it down and ask your teacher. Do not change
account or use another student's session.

### Step 5: Confirm your current folder

- [ ] Run:

```bash
pwd
```

**Why:** file actions happen in the current folder. You need to know where it is.

**Expected result:** `/home/kali`, or another folder your teacher confirms.

**If you are in the wrong folder:** run `cd ~` and then `pwd` again. If the
expected lab folder is `~/practice-files`, use `cd ~/practice-files`.

### Step 6: Confirm the expected lab files are visible

- [ ] Run:

```bash
ls
```

**Why:** this shows whether the folder contains the expected files or folders.

**Expected result:** the folders or files named in the activity, such as
`Desktop`, `Documents`, and `Downloads` in the home folder.

**If a file is missing:** check `pwd` first. Do not reset the lab. If the activity
expects a file you downloaded, re-read that step and download it again only from
the assigned target.

### Step 7: Find the assigned target

- [ ] Open the exercise panel and find **Your targets:** and **Target
      Hostnames**.

- [ ] Copy the target label, hostname, IP address, and port into your Target
      Card.

**Why:** the exercise panel is the source of truth for your lab.

**Expected result:** your Target Card is complete.

**If no target is shown:** stop and ask your teacher. Do not scan to discover
one.

### Step 8: Compare the target with the workbook

- [ ] Compare the hostname and port with the target named on the workbook page
      for your lab.

**For the RangeBox Network Basics lab, the workbook example is:**

```text
network.lab:8080
```

**Expected result:** the hostname and port match the workbook page.

**If they do not match:** stop. Do not run Step 9. Write down both values and ask
your teacher. Do not try both targets.

### Step 9: Confirm the service answers

- [ ] Run the connectivity check for your lab. For the Network Basics lab:

```bash
curl -I http://network.lab:8080/status.json
```

**Why:** this confirms that RangeBox can reach the one assigned service. It is a
read-only check.

**Expected result:** a response that starts with an HTTP status line, such as
`HTTP/1.1 200 OK`.

**If you see `Could not resolve host`:** check the spelling and the exercise.
Ask your teacher. Do not use a public website.

**If you see `Connection refused`:** check that the lab is running and that the
port matches the Target Card.

**If there is no response:** wait about 10 seconds, then press `Ctrl` + `C`.
Record a timeout, then check the lab status.

### Step 10: Confirm authorization and save your notes

- [ ] Say or write: "I will use only the target in my Target Card, for the
      action in this activity."

- [ ] Save your notes outside RangeBox.

**Why:** a reachable target is not authorization, and the lab desktop is
temporary.

**Expected result:** your Target Card is saved, and you can name the target and
the allowed action.

**If you are unsure whether an action is allowed:** stop and ask before running
it.

## Recovery Table

| Problem | Safe check | Next step |
|---|---|---|
| Expired session | You are returned to sign-in. | Sign in again. Your notes outside RangeBox are safe. |
| Missing file | Run `pwd` and `ls`. | Check the folder and the step. Re-download only from the assigned target. |
| Wrong directory | `pwd` shows an unexpected path. | Run `cd ~` or `cd ~/practice-files`, then `pwd`. |
| Wrong prompt | You see a Windows path or a local terminal. | Return to RangeBox and open its terminal. |
| Disconnected viewer | The desktop stops responding. | Try **Reconnect**, **Open RangeBox**, or **Expand**. If it still fails, stop and relaunch. |
| Target mismatch | The exercise panel differs from the workbook page. | Stop. Write both values down and ask. Do not scan. |
| Lab stopped | The status is not **Running**. | Choose **Start Exercise** or **Launch RangeBox**. |
| Blank viewer | The status is **Running** but the screen is blank. | Wait, then try **Reconnect** or **Fullscreen**. |

## What Success Looks Like

You are ready to continue when you can show:

- the correct OpenCyberRange tab and a **Running** lab;
- a RangeBox terminal prompt;
- the output of `whoami`, `pwd`, and `ls`;
- a completed Target Card with the target label, hostname, IP address, port, and
  workbook comparison;
- the result of the connectivity check;
- one sentence confirming that you will use only the assigned target.

This preflight has **no flag**. Your evidence is your completed Target Card and
your notes.

## Key Takeaways

- The exercise panel is the source of truth for the target.
- The RangeBox terminal is not your student device's terminal.
- Check identity and folder before you act.
- A target being reachable is not authorization.
- If the target differs from the workbook, stop and ask.
- Try **Reconnect** or **Open RangeBox** before you reset the lab.

Next: [Command Line Fluency](02_Command_Line_Fluency.md).
