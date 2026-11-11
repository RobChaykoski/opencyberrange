# RangeBox Troubleshooting and Safe Exit

This reference page helps you recover from common problems and end a session
safely. Use the **least disruptive** step first. Do not change browser or
security settings as a generic fix.

## Before You Begin

### Where to use this page

| Place | What it is | Used in this activity? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Yes, to read this page and keep your notes. |
| **Web browser** | The app that shows the OpenCyberRange page and RangeBox. | Yes. |
| **Exercise panel** | The part of the exercise page that shows status, targets, and controls. | Yes. |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Yes, when a check needs it. |
| **RangeBox terminal** | The text window inside RangeBox. | Yes, for the three checks on this page. |
| **Assigned target** | A practice server named in the current exercise. | **This page has no target of its own.** If a check uses one, use only the target shown in that exercise. |
| **Public internet** | Real websites and services outside the lab. | **No.** |

This page does **not** assign a target and does **not** ask you to scan or contact
anything. If you are in an exercise, the only target you may use is the one shown
in that exercise.

### How to use this page

- This page uses **text labels and descriptions**, not screenshots, so it works
  with screen readers and zoom. If your teacher provides screenshots, read their
  alt text.
- Start at the top of the **Recovery Ladder** and try one step at a time.
- Do not skip to a lab reset before you save your notes.
- If two safe steps do not fix the problem, stop and ask your teacher.
- Do not change browser security, antivirus, firewall, or school protections as a
  generic fix.

### The only commands on this page

These are checks you already know. Run them in the **RangeBox terminal**, not on
your student device.

```bash
pwd
whoami
ls
```

They have no replaceable values and no options. Type them exactly as shown.

### What you will be able to do

By the end of this activity, you will be able to:

- describe a symptom and choose a safe check;
- recover from a blank screen, loading delay, unresponsive window, wrong prompt,
  command error, lost target, disconnected session, or unsaved notes;
- order recovery from least disruptive to most disruptive;
- explain the difference between save, logout, disconnect, close, exit, stop, and
  reset;
- clean up credentials, personal information, downloaded files, and open
  sessions before you leave.

## Words to Know

| Term | What it means |
|---|---|
| **Symptom** | What you see or experience when something is wrong, such as a blank screen or an error message. |
| **Recovery** | The steps you take to get back to a safe, working state, starting with the least disruptive check. |
| **Save** | Write your notes or work to a place that survives the lab, such as your notes file. The lab desktop is temporary. |
| **Logout** | End your OpenCyberRange login session. Use the **Logout** button in the platform sidebar. |
| **Disconnect** | Lose or close the remote viewer connection. The lab may keep running. |
| **Close** | Close an application window, browser tab, or viewer. It is not the same as stopping the lab. |
| **Exit** | Leave the exercise panel. The lab keeps running. |
| **Stop** | End the exercise or RangeBox session. Unsaved work may be lost. |
| **Lab reset** | Stop the exercise and launch it again to get a fresh environment. Unsaved work may be lost. |
| **Unsaved work** | Work that exists only in the temporary lab or an open window and may be lost if the lab resets. |
| **Session expired** | The platform has ended your signed-in session, often after inactivity. Sign in again. |
| **Cleanup** | Removing or securing practice files, credentials, personal information, and open sessions at the end of an activity. |

## Seven Actions That Are Not the Same

| Action | What it affects | Does it stop the lab? |
|---|---|---|
| **Save your notes** | Your notes file outside RangeBox. | No. |
| **Logout** | Your OpenCyberRange login session. | Not automatically. Stop the lab first if you are finished. |
| **Disconnect** | The viewer connection between your browser and the remote desktop. | Not necessarily. The lab may keep running. |
| **Close an application window** | That application only. | No. RangeBox and the lab stay open. |
| **Exit the exercise panel** | The panel view. | No. The lab keeps running. |
| **Close the browser tab or viewer** | Your local view. | Not necessarily. The lab may keep running, but you lose the view. |
| **Stop Exercise or Stop RangeBox** | The lab or RangeBox session. | **Yes.** Unsaved work may be lost. |
| **Lab reset** | The lab environment. | **Yes.** It stops and starts a fresh lab. Unsaved work may be lost. |

The safest habit: **save first, then stop the lab, then close the view, then log
out** if you are on a shared device.

## Recovery Ladder

Try the lowest level that fits the symptom. Move down only if the lower level
does not work.

### Level 1: Pause and check

- Wait a few seconds.
- Read the status on the exercise page.
- Check whether the page says **Starting**, **Running**, or **Stopped**.
- Do not click the launch button repeatedly.

### Level 2: Use the built-in controls

- Click once inside the RangeBox viewer.
- Use **Expand** if the viewer is minimized.
- Use **Fullscreen** if the desktop is too small, then **Exit FS** to return.
- Use **Reconnect** if the viewer lost its connection.
- Use **Open RangeBox** in the exercise panel if the viewer is not visible.

### Level 3: Restart one application

- Switch windows with `Alt` + `Tab`.
- Close only the unresponsive application window with `Alt` + `F4`.
- Open that application again from the panel or application menu.
- Do **not** close the browser tab for an application problem.

### Level 4: Reopen the view

- Use **Close RangeBox** if it is shown, then **Open RangeBox** again.
- If the browser tab is gone, open the OpenCyberRange page again, sign in if
  needed, open the exercise, and use **Open RangeBox**.
- Your notes outside RangeBox are safe.

### Level 5: Reset the lab

- Use **Stop Exercise** on the exercise panel, or **Stop RangeBox** on the
  RangeBox page.
- Wait for the status to show that it stopped.
- Use **Start Exercise** or **Launch RangeBox** to begin again.
- A fresh lab may have a new IP address. Recheck the target in the exercise
  panel before you use it.

**Save your notes before Level 5.** Unsaved work inside the desktop may be lost.

### Level 6: Ask for help

Stop and ask your teacher if:

- two safe steps did not fix the problem;
- the target in the exercise panel does not match your Target Card;
- you see another student's information;
- a credential may have been exposed;
- a browser security warning appears;
- you are unsure whether a step is safe.

Do not solve a problem by disabling security settings or installing a "fix"
tool.

## Symptom Table

| Symptom | Likely cause | Safe check | Next step |
|---|---|---|---|
| **Blank screen** | The viewer has not loaded, is minimized, or is in fullscreen with hidden controls. | Check the status. Click once inside the viewer. Look for **Expand** or **Exit FS**. | Use **Expand** or **Exit FS**, then **Open RangeBox**. If it stays blank, close the viewer and reopen it. Then use Level 5 if needed. |
| **Loading delay** | The first launch can take about a minute. The image or lab may still be starting. | Check the status. Wait and watch. Do not click repeatedly. | Wait a little longer. If it takes more than a few minutes, stop and launch again, or ask your teacher. |
| **Unresponsive window** | One application is busy or has lost focus. | Try `Alt` + `Tab` and click the window once. Check whether the rest of the desktop responds. | Close only that application window with `Alt` + `F4`, then reopen it. Do not close the browser tab. |
| **Wrong prompt** | You may be in a terminal on your student device, or in a different account or folder. | Run `pwd` and `whoami`. A Windows path such as `C:\Users\...` means you are not in the RangeBox terminal. | Return to the RangeBox desktop and open its terminal. Do not run commands in the local terminal. |
| **Command error** | A typo, wrong case, missing space, wrong folder, or missing file. | Read the error. Run `pwd` and `ls`. Check spelling, case, and spaces. | Fix the command and try once more. Press `Ctrl` + `C` to clear a bad line. Do not paste commands from the internet or use `sudo`. |
| **Lost target** | The lab restarted, the target changed, or you are in the wrong exercise. | Check **Your targets:** and **Target Hostnames** in the exercise panel. Compare with your Target Card. | If the hostname or port differs from the workbook example, stop and ask. If the lab restarted, recheck the target before continuing. Do not scan. |
| **Disconnected session** | The viewer lost its connection or your platform session expired. | Look for **Reconnect**. Check the status and whether you are still signed in. | Use **Reconnect**. If it does not return, use **Open RangeBox**. If the session expired, sign in again. Then use Level 5 if needed. |
| **Unsaved notes** | Notes were written only inside the temporary desktop or an open window. | Check whether the notes are still visible. Copy the text to your notes file outside RangeBox. | Save before any reset. If the lab already reset, reconstruct what you can from memory and the terminal history. You may not be able to recover the original. Keep notes outside RangeBox next time. |

## After Each Recovery Step

Ask yourself:

- Did the status change?
- Did the desktop or window respond?
- Is the target still the one in my Target Card?
- Are my notes saved outside RangeBox?
- Did I stop at the least disruptive step that worked?

If the answer to any of these is no, do not jump straight to a lab reset. Try the
next safe check or ask your teacher.

## Final Cleanup Check

Complete this checklist before you leave, especially on a shared device.

- [ ] My notes are saved in my notes file, outside RangeBox.
- [ ] My notes do not contain a password, token, or other credential.
- [ ] My notes and screenshots do not contain real personal information.
- [ ] If I copied sensitive text, I overwrote the clipboard with harmless text.
- [ ] I know which practice files I downloaded or created.
- [ ] I removed only the files I created, after checking `pwd` and `ls`.
- [ ] I left unknown files in place and told my teacher about them.
- [ ] I stopped the lab with **Stop Exercise** or **Stop RangeBox**, or I know
      why it is still running.
- [ ] I closed the RangeBox viewer and any extra browser tabs I opened.
- [ ] On a shared device, I used **Logout** in the platform sidebar.
- [ ] No other student's session or account is left open on this device.

### Cleaning up files safely

If you need to remove a practice file:

1. Run `pwd` and confirm you are in the folder where you created it.
2. Run `ls` and identify the exact file.
3. Remove only that file with `rm FILE`, replacing `FILE` with the exact name.
4. Run `ls` again to verify.

Do **not** use `rm *`, `rm -r`, or `rm -rf`. Do not delete a file you do not
recognise. If you are unsure, leave it and tell your teacher.

### Cleaning up credentials and personal information

- Do not leave a password in your notes, a screenshot, or the clipboard.
- If a screenshot shows a password or personal information, redact it or delete
  that copy only if your teacher agrees it is not needed as evidence.
- If a credential was exposed, tell a trusted adult and change it through the
  official process. Do not reuse the same password.
- Do not post screenshots of your session in a group chat or on social media.

## If You Are Unsure

- If you are unsure whether your notes are saved, **do not reset**. Copy them
  first.
- If you are unsure whether the target is correct, **stop and ask**. Do not try
  another target.
- If you are unsure whether a browser change is safe, **do not make it**. Ask
  your teacher.
- If you are unsure whether the lab has stopped, check the status. Use **Stop
  Exercise** or **Stop RangeBox** if you are finished.
- If you are unsure whether you are logged out, open the sidebar and check for
  **Logout**.
- If you see another student's information, **stop, do not copy it, and tell a
  trusted adult**.
- If a credential may have been exposed, **tell a trusted adult early**. Do not
  hide it.

## What Not to Do

Do not use these as generic fixes:

- disabling browser security, antivirus, firewall, or school protections;
- installing an extension or a "fix" tool;
- clearing all browser data as a first step;
- switching browsers without asking;
- sharing a password or a screenshot of a password;
- scanning, trying other ports, or contacting another target;
- deleting unknown files or using a wildcard;
- resetting the lab again and again without asking for help.

These actions can hide the real problem, remove evidence, or move you outside the
authorized lab.

## Record Your Evidence

If something went wrong, record:

| Question | Your answer |
|---|---|
| What symptom did you see? | |
| Which recovery level did you try first? | |
| What did you see after that step? | |
| What did you do next? | |
| Were your notes saved outside RangeBox? | |
| How did you leave the session? | |

If nothing went wrong, describe how you would handle:

1. a blank screen;
2. an unresponsive application window;
3. unsaved notes before a reset;
4. a target that does not match your Target Card.

## What Success Looks Like

You are ready to finish when you can show:

- a completed cleanup checklist;
- one sentence explaining which recovery level you used and why;
- one sentence explaining the difference between closing the browser tab and
  stopping the lab;
- one sentence explaining where your notes are saved;
- one example of a problem that needs you to stop and ask instead of trying
  another fix;
- a clear statement that this page did not assign or contact a target.

This activity has **no flag**. Your evidence is your checklist and your
explanations.

## Key Takeaways

- Start with the least disruptive recovery step.
- Save notes outside RangeBox before you close or reset anything.
- **Logout** ends your platform session. **Disconnect** loses the viewer
  connection. **Close** closes a window or tab. **Exit** leaves the panel.
  **Stop** ends the lab. A **lab reset** stops and relaunches it.
- Closing the browser tab is not the same as stopping the lab.
- If the target changes or does not match your Target Card, stop and ask. Do not
  scan.
- Do not use browser or security changes as generic fixes.
- Clean up credentials, personal information, downloaded files, and open
  sessions before you leave.
- On a shared device, **Logout** so the next student does not inherit your
  session.

This is the end of the troubleshooting reference. Return to your current
exercise, or continue with [Chapter Review](10_Chapter_Review.md).
