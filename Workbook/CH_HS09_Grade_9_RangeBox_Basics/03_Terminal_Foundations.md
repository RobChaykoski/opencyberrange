# Terminal Foundations

This extra practice activity is your first careful lesson in the RangeBox
terminal. You will learn what the terminal, the shell, the prompt, and a command
are, then run four harmless commands one at a time.

## Before You Begin

Complete [Signing In and Opening RangeBox](01_First_Steps.md) first. You should
already have the RangeBox desktop open and a terminal available.

### Where to run this activity

| Place | What it is | Used in this activity? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | No. Do not run these commands in a terminal on your own device. |
| **Web browser** | The app that shows the OpenCyberRange page. | Only to view the page. |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Yes. This is where the terminal lives. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Target** | The practice server named in an activity. | **Not used in this activity.** These commands do not contact a server. |

Later activities name their own target, such as `rangebox.lab:8080` or
`files.lab:8080`. Use only the target shown in that activity. In this activity
you stay inside the RangeBox terminal and do not use the network.

!!! warning "Stay in the RangeBox terminal"
    Do not open a terminal on your own device. Do not type commands from the
    internet. Use only the commands in this page, and ask your teacher if you
    are unsure.

### What you need

- [ ] The RangeBox desktop open from the first activity.
- [ ] The RangeBox terminal open.
- [ ] A notes file for what you type and what you see.
- [ ] About **10–15 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain the difference between the terminal, the shell, and the prompt;
- identify the command, option, argument, output, and cursor in a terminal;
- type a command exactly, including spaces and hyphens;
- run `pwd`, `whoami`, `date`, and `ls` one at a time;
- explain what each line of output means;
- recover from a typing mistake, a command-not-found message, or a
  frozen-looking terminal.

## Words to Know

Read this table before you type anything. Every term is used in the activity.

| Term | What it means |
|---|---|
| **Terminal** | The text window where you type commands. |
| **Shell** | The program inside the terminal that reads your command, runs it, and prints the result. |
| **Prompt** | The text at the start of a terminal line that shows the shell is ready for a command. It often shows your account and current folder, and often ends with `$`. Do not type the prompt. |
| **Command** | The instruction you type. The command name is usually the first word. |
| **Option** | A setting that changes how a command works. It often starts with a hyphen, such as `-l`. This activity's commands do not use options. |
| **Argument** | Extra information a command acts on, such as a file name or a folder name. This activity's commands do not use arguments. |
| **Output** | The text the command prints after you press `Enter`. |
| **Cursor** | The blinking line or block that shows where your typing will appear. |
| **Enter key** | The key you press to run the command. |
| **Case sensitivity** | Treating uppercase and lowercase letters as different. Linux command names are usually lowercase, so `pwd` and `PWD` are not the same command. |
| **Space** | The gap between words. Leave one space between the command and any option or argument. |
| **Hyphen** | The `-` character. Do not put a space between a hyphen and the letter after it. |
| **Replaceable value** | A word in capitals, such as `FILE` or `FOLDER`, that you replace with a real name. This activity's commands have no replaceable values. |
| **Command not found** | A message that means the shell could not find a command with that exact spelling. |

## The Terminal, the Shell, and the Prompt

These three words are easy to mix up.

- The **terminal** is the window you see.
- The **shell** is the program inside the window that does the work.
- The **prompt** is the shell's way of saying, "I am ready. Type here."

When you press `Enter`, the shell reads the line, runs the command, and prints
the **output**. When it is finished, it shows the prompt again. That cycle is
the whole terminal lesson:

```text
prompt → type a command → press Enter → read the output → prompt returns
```

If you see output but no new prompt, the command may still be running. Wait
before typing again.

## Reading a Command

A command is made of parts. You do not need to run these examples; they show you
how to read a command you will meet later.

```text
ls
│
└─ command name
```

```text
cat FILE
    │
    └─ argument: replace FILE with a real file name
```

```text
ls -l
   │
   └─ option: a setting that changes the output
```

Three rules prevent most typing mistakes:

1. **Use one space** between the command and the next part. Do not use a space
   inside a command name.
2. **Keep a hyphen attached** to its letter, as in `-l`. Do not type `- l`.
3. **Replace a word in capitals** with a real name. Do not type the capital word
   itself.

In this activity, every command is short and has no options or arguments. Type
it exactly as shown, then press `Enter`.

## Walkthrough: Four Safe Commands

Run one command at a time. After each command, read the output before you type
the next one.

### Step 1: Find the prompt and the cursor

Look at the terminal. Find the prompt and the cursor.

**You should see:** a line of text ending with a symbol such as `$`, followed by
a blinking cursor. The cursor may be a line or a block.

Do not type the prompt. Type only after the prompt.

### Step 2: Run the location command

Type this command exactly and press `Enter`:

```bash
pwd
```

**You should see:** one line with a folder path, such as `/home/kali`. Your path
may be different.

Read the line like this:

- `/` separates folder names.
- The path starts at the top of the file system and ends at the folder you are
  in now.
- `/home/kali` means the home folder of the practice account.

`pwd` stands for "print working directory". A **directory** is another word for
a folder.

### Step 3: Run the identity command

Type this command exactly and press `Enter`:

```bash
whoami
```

**You should see:** one short line with the account name used inside RangeBox,
such as `kali`. Your practice desktop may use a different account name.

This is the **RangeBox account**, not your OpenCyberRange login. Never type your
OpenCyberRange password into the terminal.

### Step 4: Run the date command

Type this command exactly and press `Enter`:

```bash
date
```

**You should see:** one line with the current date and time, in a form like:

```text
Tue Nov 11 09:42:17 UTC 2026
```

Your date, time, and time zone will be different. Read the line from left to
right: weekday, month, day, time, time zone, year. The desktop clock, not your
local device, decides this value.

### Step 5: Run the listing command

Type this command exactly and press `Enter`:

```bash
ls
```

**You should see:** the names of folders or files in your current folder, such
as `Desktop`, `Documents`, and `Downloads`. The exact names may be different.

Read the output like this:

- Each name is an item in the current folder.
- `ls` does not open or change anything. It only lists names.
- If the folder is empty, `ls` may print nothing and return to the prompt. That
  is a normal result, not an error.

### Step 6: Return to the prompt

After each command, wait for the prompt to come back before typing the next
command.

**You should see:** the prompt and the cursor on a new line, ready for your next
command.

You have now completed the four commands. This activity has **no flag**. Your
evidence is your notes and your explanation.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| A typing mistake | The wrong letters in the line | Press `Backspace` to delete. If the line is very wrong, press `Ctrl` + `C` to cancel it and get a fresh prompt. |
| Command not found | `command not found` or a similar message | Check the spelling, the case, and the spaces. Type the command again exactly as shown. |
| The command seems to do nothing | Output but no new prompt | Wait a moment. If the prompt still does not return, do not close the browser. Use **Stop Exercise** and launch the exercise again. |
| The terminal shows `>` at the start of a line | A continuation prompt | The shell may be waiting for the rest of a command. Press `Ctrl` + `C` to cancel and return to the normal prompt. |
| You cannot see the cursor | A blank or still screen | Click once inside the terminal window. If it still does not respond, ask your teacher. |
| You accidentally ran a command in your own device's terminal | Output from your own computer | Stop. Close that terminal and return to the RangeBox terminal. If you are unsure what happened, tell your teacher. |
| The terminal closes | The window disappears | Open the terminal again from the panel or application menu. RangeBox is still running. |
| RangeBox disconnects | The viewer stops responding | Use **Reconnect** if shown, or stop and relaunch the exercise. Your notes outside the desktop are safe. |

**Do not** try to fix an error by adding commands you found online. Ask your
teacher or use the recovery step in the table.

## Record Your Evidence

Copy this table into your notes and fill it in.

| Command | What I expected | What I saw | What it means in my own words |
|---|---|---|---|
| `pwd` | | | |
| `whoami` | | | |
| `date` | | | |
| `ls` | | | |

Then answer these questions.

1. Which window is the terminal, and which window is the OpenCyberRange page?
2. What is the difference between the terminal and the shell?
3. What does the prompt tell you?
4. Why does `PWD` not work when `pwd` does?
5. What should you do if you see `command not found`?
6. What should you do if the terminal seems frozen?
7. Did any command in this activity contact a target? Explain your answer.

## What Success Looks Like

You are ready to continue when you can show:

- the four commands typed exactly, with their output;
- a note explaining what `pwd`, `whoami`, `date`, and `ls` each do;
- a clear statement that the commands ran in the RangeBox terminal, not on your
  own device;
- a clear statement that this activity did not use a network target;
- one recovery step you would use after a typing mistake or a command-not-found
  message.

A strong answer can explain that the terminal is the window, the shell is the
program that runs commands, the prompt shows the shell is ready, and the output
is the result.

## Key Takeaways

- The terminal is the window; the shell is the program inside it.
- The prompt means the shell is ready. Do not type the prompt.
- Type commands exactly, use one space, and keep hyphens attached.
- Linux command names are usually lowercase and case-sensitive.
- `pwd` shows your location, `whoami` shows your RangeBox account, `date` shows
  the desktop's date and time, and `ls` lists the current folder.
- An error message is information. Read it, check the spelling and spaces, and
  try again.
- Your notes and explanation are the evidence, not only a completed command.

When you are ready, continue with [RangeBox File Hunt](02_File_Hunt.md).
