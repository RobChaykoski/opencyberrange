# High School Cybersecurity — Grade 9 RangeBox Basics

## Welcome

This chapter is your first step into a safe practice space for this subject. It
is written for students who use a computer every day but have not studied this
subject before. You do not need any special technical knowledge or software
installation.

The chapter has eight core activities and seven extra-practice pages. You will
open a practice desktop, use the on-screen tools, decode a few messages, and
practise checking a link or file before you click or open it. You can work at
your own pace.

## Words to Know

Read this table before you start. Every term is explained in plain language, and
you will see these words in the activities.

| Term | What it means |
|---|---|
| **Cybersecurity** | Keeping computers, accounts, and information safe. It includes defence and careful investigation. |
| **Cyber range** | A safe, separate practice space for cybersecurity. The computers inside are for practice, not real-world targets. |
| **OpenCyberRange** | The platform your class uses to open exercises and the practice desktop. |
| **Operating system** | The main software that runs a computer, such as Windows or macOS. |
| **Linux** | A type of operating system used by the practice desktop. You do not need Linux experience to start. |
| **Kali Linux** | A Linux distribution used for cybersecurity practice. Choose the Kali desktop when you are asked which desktop to open. |
| **Browser** | The app you use to visit websites, such as Chrome, Edge, Firefox, or Safari. |
| **Browser tab** | One page area inside your browser. Keep the exercise tab open while you work. |
| **RangeBox** | The temporary Linux desktop the platform provides for the activities. It has a text window and tools. |
| **Virtual machine** | A computer that runs inside another computer. A lab desktop provided through the web is not installed on your device. |
| **Exercise** | One activity in OpenCyberRange with instructions and, sometimes, a submission code. |
| **Lab** | The temporary practice environment for an exercise. |
| **Desktop** | The screen with windows, icons, and open apps. |
| **Terminal** | A text window where you type instructions. |
| **Command** | An instruction you type into a terminal. |
| **Command prompt** | The place in the terminal where you type. It often shows your login name and where you are working. |
| **Server** | A computer that provides something to other computers, such as a web page. |
| **Target** | The practice server assigned to the activity. It is the only computer you may use in that activity. |
| **Scope** | The systems and actions you are allowed to use in an activity. |
| **Account** | Your OpenCyberRange login. Keep your password private. |
| **Authorized activity** | The work your teacher or the platform asks you to do inside OpenCyberRange. If you are unsure, stop and ask first. |
| **File** | A named piece of data, such as a document, picture, or text file. |
| **Folder** | A container that holds files. |
| **Link** | Clickable text or an image that opens a page in your browser. |
| **URL** | A web address, such as the address of a page or file. |
| **Decode** | Change encoded or scrambled data back into a form you can read. |
| **Encode** | Change data into another form. Encoding does not keep data secret. |
| **Taskbar** | The bar on the desktop that shows open apps and shortcuts. |
| **Application menu** | The menu used to open programs on the desktop. |
| **Clipboard** | A temporary place for copied text. RangeBox has a Clipboard button for moving text between the browser and the desktop. |
| **Accessibility options** | Ways to make an activity easier to use, such as zoom, keyboard navigation, less motion, or extra time. |
| **Reduced motion** | A device setting that reduces animation and motion effects. |
| **Hint** | A clue that helps you take the next step without giving the whole answer. |
| **Flag** | A code in `OCR{...}` format that shows you completed a challenge. Submit it in the platform when an activity asks for it. |

## What You Will Learn

By the end of this chapter, you will be able to:

- open RangeBox and find the terminal;
- type simple commands and read what they print;
- explain which computer is the target and why only that computer is in scope;
- use hints and ask for help without guessing;
- stop and relaunch the lab if something is not working;
- check a link or file before you click or open it;
- explain authorization, privacy, and responsible reporting;
- describe a concern without copying or sharing sensitive data;
- distinguish a mistake from intentional harm and know when to stop and ask for
  help;
- explain a decision you made, not just report a flag.

## What You Need

- A laptop or desktop computer with a browser. RangeBox is built for a keyboard
  and a larger screen. A tablet with a keyboard may work, but a phone is not
  recommended for the desktop activities.
- Your OpenCyberRange account. Your teacher will tell you how to sign in. Do not
  share your password.
- The exercise page open in the platform.
- RangeBox, or the lab browser or terminal your teacher provides as a fallback.

## Estimated Time

Plan for about **2–3 hours across all eight activities**. Each activity is short,
and you can split them across several sessions. The first RangeBox launch can
take about a minute while the desktop starts; that is normal. This is a planning
estimate, not a deadline.

## How to Launch RangeBox

1. Open one of the High School exercises.
2. Choose **Launch RangeBox**.
3. Pick the **Kali** desktop.
4. Wait for the desktop to finish loading.
5. Open the terminal from the taskbar or the application menu.

If RangeBox is not available on your deployment, use the lab browser or the
terminal your teacher provides. The activity pages explain what to do in either
case.

## What You May Do

- Launch the exercise and use the RangeBox desktop.
- Run the commands shown in the activities.
- Use hints whenever you are stuck.
- Ask your teacher or classmates for help with the task.
- Take breaks.
- Stop the lab and launch it again if you need a fresh start.

## What to Avoid

These rules keep the practice fair and keep everyone's devices safe.

- Use only the target shown in your exercise. Do not use the commands on your
  own device, your school network, another student's lab, or the internet.
- Do not share your account or password.
- Do not enter real personal information, real passwords, or private messages
  into the practice desktop.
- Do not click or open real suspicious links or files outside the lab. The
  activities use safe, fictional examples.
- If you are unsure whether something is allowed, stop and ask your teacher.
  Asking is part of the work, not a mistake.

## How to Ask for Help

1. Read the step again and check for a typo.
2. Open the **Hint** for that activity.
3. Write down three things: the step, what you expected, and what happened.
4. Ask your teacher and show the screen if you are allowed. Do not share your
   password.
5. If you feel stuck or unsafe, stop. You can return to the activity later.

Errors are information. They tell you that a command, a folder name, or a
connection did not work as expected. Read the message before trying again.

## How to Reset the Lab

If the desktop or lab stops responding:

1. Use **Stop Exercise** in the exercise panel, or **Stop RangeBox** on the
   RangeBox page.
2. Wait for the status to show that it has stopped.
3. Launch the exercise again. You will get a fresh practice environment.
4. Ask your teacher before refreshing the browser if you are not sure.

Keep your notes in your workbook or notes file, not only inside the temporary
desktop. The desktop is a practice space and may be replaced when you relaunch.

## Accessibility Options

You can make the activities easier to use:

- **Zoom:** use your browser's zoom controls, or `Ctrl` + `+` / `Ctrl` + `-`
  (`Cmd` + `+` / `Cmd` + `-` on a Mac).
- **Keyboard:** use `Tab` and `Shift` + `Tab` to move between links and buttons,
  and `Enter` to activate them.
- **Reduced motion:** turn on your device's reduced-motion setting if animation
  bothers you. The platform respects that setting.
- **Copy and paste:** use the **Clipboard** button in RangeBox to move text
  between the browser and the desktop. You can copy a command from the workbook
  instead of retyping it.
- **Time and breaks:** take breaks and ask your teacher about extra time. The lab
  has a timer, so check with your teacher if you need more time.
- **Other support:** if you use a screen reader or another assistive tool, tell
  your teacher what you need. Ask for help if an instruction or label is unclear.

## A Few Terminal Basics

A **terminal** is a text window. You type a command, press `Enter`, and read what
the computer prints. You do not need to memorise these commands; use this table
as a reference.

| Command | What it does | What to replace |
|---|---|---|
| `pwd` | Prints the folder you are currently in. | Nothing. Type it as shown. |
| `ls` | Lists the files in the current folder. | Nothing. Type it as shown. |
| `whoami` | Prints your account name. | Nothing. Type it as shown. |
| `cd FOLDER` | Moves into a folder. | Replace `FOLDER` with a real folder name. |
| `cat FILE` | Prints the contents of a text file. | Replace `FILE` with a real file name. |
| `curl URL` | Requests a web page or file. | Replace `URL` with the address shown in the activity. |

Use lowercase for the command names. Type the command, replace any uppercase
word with the real name, and press `Enter`. If a command prints an error, read
the message and check the spelling and the part you replaced.

## A Safe Place to Practise

- Every target in this chapter is fictional.
- You cannot break the practice server.
- Using hints is part of learning.
- You can pause, ask for help, or stop at any time.
- If a command produces an error, read the error before trying again.

The last three activities form a digital-safety unit (habits that protect you
online). You will read a link without clicking it, check what a file really is
before opening it, and combine both habits in a short final activity. The goal is
a decision you can explain, not just a flag.

## Success Evidence

You are ready to move on when you can show:

- a note with the command you ran, what it printed, and one sentence explaining
  it;
- the flag for an activity, if the activity has one, submitted in the platform;
- a clear explanation of which computer was the target and where you ran the
  commands;
- one example of a link or file you checked before clicking or opening it.

A flag shows that you reached the end of an activity. Your notes and explanation
show that you understand what you did.

## Confidence Check

This is not a test and it is not graded. It helps you decide what to ask for.
Mark one box for each statement.

| I can… | Not yet | Almost | Yes |
|---|---|---|---|
| Say where commands are typed in this chapter. | [ ] | [ ] | [ ] |
| Name the target for an activity. | [ ] | [ ] | [ ] |
| Explain what “authorized activity” means. | [ ] | [ ] | [ ] |
| Read a command error and decide what to check next. | [ ] | [ ] | [ ] |
| Ask for help without sharing my password. | [ ] | [ ] | [ ] |
| Stop the lab and launch it again. | [ ] | [ ] | [ ] |

If you mark **Not yet** or **Almost**, that is useful information. Ask your
teacher or revisit the activity before moving on.

## Activities

1. [Signing In and Opening RangeBox](01_First_Steps.md) — sign in, open the
   desktop, and try simple terminal commands.
2. [RangeBox File Hunt](02_File_Hunt.md) — find a file in the practice desktop.
3. [CyberChef: Decode a Base64 Message](03_CyberChef_Base64.md) — use CyberChef
   (a browser tool for decoding data) to decode Base64 (a common way to change
   text into another form; it does not keep the text secret).
4. [CyberChef: Read a Caesar Shift](04_CyberChef_Caesar.md) — read a Caesar shift
   (a simple secret-code method that moves each letter by a fixed number of
   places).
5. [CyberChef: Peel Back Two Layers](05_CyberChef_Layers.md) — combine two
   decoding steps.
6. [Read the Link Before You Click](06_Read_The_Link.md) — inspect a link before
   opening it.
7. [Know the File Before You Open It](07_Know_The_File.md) — check what a file is
   before opening it.
8. [Capstone: The Forwarded Message](08_Forwarded_Message.md) — combine the
   digital-safety habits in one decision. A capstone is a final activity that
   brings the earlier skills together.

### Extra Practice

These seven pages are optional. They help you get comfortable with the desktop,
the terminal, files, basic networking, safe command sequences, and responsible
decisions before you open File Hunt. They do not replace the eight core
activities.

- [RangeBox Desktop and Window Basics](02_RangeBox_Desktop_and_Window_Basics.md)
  — label the browser and RangeBox controls, then open, switch, resize, and
  safely close two approved applications.
- [Terminal Foundations](03_Terminal_Foundations.md) — learn what the terminal,
  shell, prompt, command, option, argument, and output are, then run four safe
  commands one at a time.
- [Files, Folders, and Paths](04_Files_Folders_and_Paths.md) — practise listing,
  reading, moving, copying, and removing disposable files in a sandbox folder.
- [Internet and Network Basics](05_Internet_and_Network_Basics.md) — learn what
  hosts, clients, servers, IP addresses, hostnames, protocols, services, ports,
  requests, and responses are, then make one safe read-only request.
- [Target and Connectivity Check](06_Target_and_Connectivity_Check.md) — find the
  assigned target, copy it into a labelled note, and confirm that one service
  answers before you continue.
- [Basic Command Practice](07_Basic_Command_Practice.md) — combine identity,
  location, folder, note, target, and connectivity checks in one short guided
  sequence.
- [Cyber Ethics, Privacy, and Digital Citizenship](08_Cyber_Ethics_Privacy_and_Digital_Citizenship.md)
  — use fictional school scenarios to practise authorization, privacy,
  responsible reporting, and a calm stop-and-report process.

Start with [Signing In and Opening RangeBox](01_First_Steps.md). Take it one
command at a time, and ask for help when you need it.
