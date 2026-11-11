# Troubleshooting, Reset, and Safe Exit

This reference helps you recover independently and leave the lab clean. Start
with the least disruptive check. Do not disable browser security, antivirus,
firewall, or school protections as a generic fix.

## Before You Begin

### Where to use this page

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, for notes and the browser. |
| **Exercise panel** | The area with status, targets, and controls. | Yes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | Yes, for diagnostic checks. |
| **Assigned target** | The target named in your current exercise. | **This page has no target of its own. Use only the current exercise target.** |

### The only diagnostic commands here

```bash
pwd
whoami
ls
```

They have no replaceable values and no options. Run them in the RangeBox
terminal, not on your student device.

### What you will be able to do

- recover from a wrong prompt, incorrect path, command error, permission denied,
  no network response, missing file, disconnected session, or unsaved work;
- order checks from reading the error to verifying context, command, target,
  network, application restart, and lab reset;
- stop and ask instead of experimenting;
- clean up notes, screenshots, credentials, downloaded files, terminal history,
  and active sessions.

## Words to Know

| Term | What it means |
|---|---|
| **Symptom** | What you see when something is wrong. |
| **Likely cause** | The most probable reason for the symptom. It is not proof. |
| **Recovery** | The steps that return you to a safe working state. |
| **Lab reset** | Stopping and relaunching the exercise. Unsaved work may be lost. |
| **Unsaved work** | Work that exists only in the temporary lab or an open window. |
| **Cleanup** | Securing notes, files, credentials, and sessions before you leave. |

## Recovery Ladder

Try the lowest level first.

### Level 1: Read the error

- Read the whole message.
- Identify the command, path, target, or permission it mentions.
- Do not retype the command immediately.

### Level 2: Verify context

```bash
pwd
whoami
ls
```

Check:

- Are you in the RangeBox terminal?
- Are you in the expected folder?
- Are the expected files present?
- Are you using the expected account?

### Level 3: Verify the command and target

- Compare the command with the workbook.
- Check spelling, case, spaces, quotes, and options.
- Compare the target with the exercise panel and your Target Card.
- If the target differs, stop and ask.

### Level 4: Check the network

- Is the lab status **Running**?
- Does the service answer?
- Is the port the one named in the exercise?
- Is the failure a name-resolution, refused, timeout, or filtered result?

### Level 5: Restart one application

- Use `Alt` + `Tab` to switch windows.
- Close only the unresponsive application with `Alt` + `F4`.
- Reopen it from the RangeBox panel or application menu.
- Do not close the browser tab for an application problem.

### Level 6: Reopen the viewer

- Use **Reconnect**.
- Use **Open RangeBox**.
- Use **Expand** or **Fullscreen** if the viewer is hidden.
- If the browser tab is gone, reopen the OpenCyberRange page and the exercise.

### Level 7: Reset the lab

- Save your notes outside RangeBox.
- Use **Stop Exercise** or **Stop RangeBox**.
- Wait for the status to show that it stopped.
- Use **Start Exercise** or **Launch RangeBox**.
- Recheck the target; a fresh lab may have a new IP address.

### Level 8: Ask for help

Stop and ask if:

- two safe steps did not fix the problem;
- the target differs from the workbook;
- you see another student's data;
- a credential may be exposed;
- a browser security warning appears;
- you are unsure whether an action is safe.

## Symptom Table

| Symptom | Likely cause | Safe check | Next step |
|---|---|---|---|
| **Wrong prompt** | You are in a local terminal or a different account/folder. | Run `pwd` and `whoami`. A Windows path such as `C:\Users\...` is local. | Return to the RangeBox terminal. Do not run commands locally. |
| **Incorrect path** | You are in the wrong folder, or a path has a typo or wrong case. | Run `pwd` and `ls`. | Use `cd` to the correct folder. Check case and spelling. |
| **Command error** | Typo, wrong option, missing argument, or wrong command. | Read the error. Compare with the workbook. | Fix one thing and retry once. Press `Ctrl` + `C` to clear a line. |
| **Permission denied** | You do not have read, write, or execute permission. | Run `ls -l` on the exact file or folder. | Work only in your practice folder. Do not use `sudo`. Ask if unsure. |
| **No network response** | Lab stopped, wrong target, wrong port, name resolution, timeout, or filter. | Check the status, target, port, and the exact error. | Use **Reconnect** or **Open RangeBox**. If the target differs, stop. |
| **Missing file** | Wrong folder, not downloaded, or removed. | Run `pwd` and `ls`. | Re-download only from the assigned target, or ask. |
| **Disconnected session** | Viewer connection lost or platform session expired. | Check the status. Look for **Reconnect**. | Reconnect, then **Open RangeBox**. If the session expired, sign in again. |
| **Unsaved work** | Notes were only inside the temporary desktop. | Check whether the notes are still visible. | Copy them outside before any reset. If lost, reconstruct and tell your teacher. |

## Save, Logout, Disconnect, Close, Exit, Stop, Reset

| Action | What it affects | Does it stop the lab? |
|---|---|---|
| **Save notes** | Your notes file outside RangeBox. | No. |
| **Logout** | Your OpenCyberRange login session. | Not automatically. Stop the lab first. |
| **Disconnect** | The viewer connection. | Not necessarily. |
| **Close an application** | One application window. | No. |
| **Exit** | The exercise panel view. | No. The lab keeps running. |
| **Close the browser tab** | Your local view. | Not necessarily. |
| **Stop Exercise** / **Stop RangeBox** | The lab or desktop. | **Yes.** Unsaved work may be lost. |
| **Lab reset** | The lab environment. | **Yes.** It stops and starts fresh. |

The safe habit: **save notes, stop the lab, close the view, then Logout** on a
shared device.

## Final Cleanup Check

- [ ] Notes are saved outside RangeBox.
- [ ] Notes contain no passwords, tokens, or real personal information.
- [ ] Screenshots show only necessary context and are redacted.
- [ ] Clipboard contains no sensitive text.
- [ ] I know which practice files I downloaded or created.
- [ ] I removed only my own files, after checking `pwd` and `ls`.
- [ ] Unknown files are left in place and reported.
- [ ] The lab is stopped, or I know why it is running.
- [ ] RangeBox and extra tabs are closed.
- [ ] I used **Logout** on a shared device.
- [ ] No other student's session is open.

### Clean up files safely

1. `pwd` and confirm the folder.
2. `ls` and identify the exact file.
3. `rm FILE`, replacing `FILE` with the exact name.
4. `ls` again.

Do not use `rm *`, `rm -r`, or `rm -rf`. Do not delete unknown files.

### Clean up terminal history and notes

- Remove pasted passwords or personal data from your notes.
- If you copied a secret, overwrite the clipboard with harmless text.
- Do not post terminal output or screenshots in a group chat.
- If a credential was exposed, tell a trusted adult and change it through the
  official process.

## If You Are Unsure

- Unsure whether notes are saved? Do not reset. Copy them first.
- Unsure whether the target is correct? Stop and ask.
- Unsure whether a browser change is safe? Do not make it.
- Unsure whether the lab stopped? Check the status.
- See another student's data? Stop, do not copy it, and tell a trusted adult.
- A credential exposed? Tell a trusted adult early.

## What Success Looks Like

You can show:

- one symptom, likely cause, safe check, and next step;
- one sentence explaining why you chose that recovery level;
- one sentence explaining the difference between closing the tab and stopping the
  lab;
- a completed cleanup checklist;
- a clear statement that you did not change browser or security settings.

This page has **no flag**. Your evidence is your recovery note and checklist.

## Key Takeaways

- Read the error before you retry.
- Check context, command, target, network, then restart.
- Save notes before a reset.
- Closing a tab is not stopping the lab.
- Stop and ask when the target, data, or action is unclear.
- Clean up files, credentials, screenshots, and sessions.

Next: [Chapter Review](11_Chapter_Review.md).
