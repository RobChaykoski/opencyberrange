# Command Line Fluency

This activity builds confidence with the command line using **disposable local
files**. It does not use a network target. You will learn how a command is put
together, how output and errors are separated, and how pipes and redirection
change what you see.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Assigned target** | A practice server named in a lab. | **None. This activity is local to RangeBox.** |

This activity does **not** contact a target. Do not run these commands on your
student device.

### What you need

- [ ] The RangeBox terminal open.
- [ ] A notes file for predictions and results.
- [ ] About **25–35 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain executable, option, argument, output, exit status, standard input,
  standard output, and standard error;
- use quotes, spaces, wildcards, and case sensitivity correctly;
- redirect output and error to a disposable file;
- connect two commands with a pipe;
- use command history and `Ctrl` + `C` safely;
- follow a predict, execute, verify, and correct cycle.

## Words to Know

| Term | What it means |
|---|---|
| **Executable** | The program a command name starts. For example, `ls` starts the `ls` program. |
| **Option** | A setting that changes how a command works, often starting with `-`, such as `-l`. |
| **Argument** | Extra information a command acts on, such as a file name. |
| **Standard output (stdout)** | The normal result a command prints. |
| **Standard error (stderr)** | Error messages a command prints. |
| **Standard input (stdin)** | Data a command reads, often from the keyboard or another command. |
| **Exit status** | A number a command returns to the shell. `0` usually means success; a nonzero number usually means failure. |
| **Pipe (&#124;)** | Sends the standard output of one command into the standard input of another. |
| **Redirection (`>`)** | Sends output to a file instead of the screen. `>` replaces; `>>` appends. |
| **Wildcard (`*`)** | A pattern that matches many names. Use it carefully, especially with delete commands. |
| **Command history** | The shell's record of commands you have run. |
| **Case-sensitive** | Uppercase and lowercase are different. `note.txt` and `Note.txt` are different names. |

## The Four-Part Cycle

For every command in this activity:

1. **Predict:** write what you think will happen.
2. **Execute:** run one command.
3. **Verify:** compare the output with your prediction.
4. **Correct:** if it differs, read the error and change one thing.

A prediction that is wrong is useful. It shows what you need to learn.

## Walkthrough

### Step 1: Create a disposable workspace

**Current directory:** check with `pwd`.

Run:

```bash
cd ~
mkdir -p cli-practice
cd cli-practice
pwd
```

**Why:** a separate folder keeps this practice away from other files.

**Expected result:** `/home/kali/cli-practice` (or the same path under your home
folder).

**If `cd` says `No such file or directory`:** run `pwd` and `ls`, then repeat
`mkdir -p cli-practice` and `cd cli-practice`.

### Step 2: Print text to standard output

**Predict:** what will this print?

```bash
echo "hello from RangeBox"
```

**Why:** `echo` is a simple executable. The quoted text is an argument.

**Expected result:**

```text
hello from RangeBox
```

**What to notice:** the text went to **standard output**, which is the terminal
screen.

### Step 3: Redirect output to a file

**Predict:** what will `cat` show?

```bash
echo "first line" > note.txt
cat note.txt
```

**Why:** `>` sends standard output to `note.txt` instead of the screen. `cat`
reads the file and prints it.

**Expected result:**

```text
first line
```

**What to notice:** the file now exists. The `>` **replaced** anything that was
already in the file.

### Step 4: Append instead of replacing

**Predict:** how many lines will the file have?

```bash
echo "second line" >> note.txt
cat note.txt
```

**Why:** `>>` adds to the end of the file instead of replacing it.

**Expected result:**

```text
first line
second line
```

### Step 5: Count lines with an option

**Predict:** what number will `wc` print?

```bash
wc -l note.txt
```

**Why:** `wc` counts words, lines, and characters. The option `-l` means "count
lines only".

**Expected result:** a number followed by the file name, such as:

```text
2 note.txt
```

### Step 6: Search with `grep`

**Predict:** which line will `grep` print?

```bash
grep "second" note.txt
```

**Why:** `grep` prints lines that contain the text you give it. `"second"` is the
pattern; `note.txt` is the argument.

**Expected result:**

```text
second line
```

### Step 7: Connect two commands with a pipe

**Predict:** what will the final number be?

```bash
cat note.txt | wc -l
```

**Why:** the pipe sends the output of `cat` into `wc`. `wc` counts the lines it
receives.

**Expected result:** `2`.

**What to notice:** `wc` has no file argument here. It reads from **standard
input**, which came from `cat`.

### Step 8: See an error on standard error

**Predict:** what will the terminal show?

```bash
ls missing-file.txt
```

**Why:** this asks `ls` for a file that does not exist. The error goes to
**standard error**.

**Expected result:** an error message such as:

```text
ls: cannot access 'missing-file.txt': No such file or directory
```

**What to notice:** the shell prompt returns. The command failed, but the terminal
is still usable.

### Step 9: Redirect the error to a file

**Predict:** what will `cat error.txt` show?

```bash
ls missing-file.txt 2> error.txt
cat error.txt
```

**Why:** `2>` sends standard error to `error.txt`. The normal output still goes to
the screen.

**Expected result:** `cat` prints the same error message from the file.

### Step 10: Check the exit status

**Predict:** what number means success?

```bash
echo "ok"
echo $?
```

**Why:** `$?` is the exit status of the previous command. `0` usually means
success.

**Expected result:** `ok`, then `0`.

Now try a failure:

```bash
ls missing-file.txt
echo $?
```

**Expected result:** the error message, then a nonzero number. The exact number
may differ.

### Step 11: Use quotes for a name with spaces

**Predict:** will `cat` find the file?

```bash
echo "quoted text" > "my note.txt"
cat "my note.txt"
ls
```

**Why:** quotes keep `my note.txt` together as one argument. Without quotes, the
shell treats `my` and `note.txt` as two arguments.

**Expected result:** `quoted text`, and `my note.txt` appears in the `ls` list.

### Step 12: Use a wildcard carefully

**Predict:** which names will `ls` show?

```bash
ls *.txt
```

**Why:** `*` matches any characters. `*.txt` means "every name that ends in
`.txt`".

**Expected result:** `error.txt`, `my note.txt`, `note.txt`, or the `.txt` files
you created.

**Safety note:** wildcards are useful for listing, but dangerous with `rm`. This
activity never uses `rm` with a wildcard.

### Step 13: See case sensitivity

**Predict:** will this find the file?

```bash
cat Note.txt
```

**Why:** Linux file names are case-sensitive. `Note.txt` and `note.txt` are
different.

**Expected result:** an error such as `No such file or directory`.

**Correction:** use the exact name, `note.txt`.

### Step 14: Use command history

At the prompt, press the **Up arrow** key. The previous command appears. Press
**Down** to move forward again.

**Why:** command history saves retyping and helps you check what you ran.

**Expected result:** an earlier command appears at the prompt. Do not press
`Enter` unless you want to run it again.

### Step 15: Cancel a command line

Type part of a command, then press `Ctrl` + `C`.

**Why:** `Ctrl` + `C` cancels the current line or command without running it.

**Expected result:** the line is abandoned and a fresh prompt appears.

## Reset This Activity

From `~/cli-practice`, remove only the files you created:

```bash
pwd
ls
rm note.txt "my note.txt" error.txt
ls
cd ..
rmdir cli-practice
```

**Why:** this removes only the disposable practice folder.

**If `rmdir` says the folder is not empty:** run `ls cli-practice` and identify
the files. Remove only files you created. If you are unsure, leave the folder and
ask your teacher. Do not use `rm -r` or a wildcard.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong folder | `pwd` is not `cli-practice` | Run `cd ~/cli-practice` or repeat Step 1. |
| File already exists | `cat` shows old text | `>` replaced it; use `>>` to append, or remove only that file. |
| Permission denied | `Permission denied` | Check `pwd` and `ls -l`. Stay in your home folder. Do not use `sudo`. |
| Command not found | `command not found` | Check spelling and case. |
| A command is waiting | No prompt | Press `Ctrl` + `C` to cancel. |
| A pipe gives unexpected output | The second command changes the input | Run each side separately, then combine. |
| A wildcard matches too much | A long list or unexpected files | Run `ls` with the pattern first. Never combine a wildcard with `rm`. |

## Record Your Evidence

Copy this table into your notes.

| Step | Prediction | Command | Result | What I learned |
|---|---|---|---|---|
| Output | | `echo` | | |
| Redirect | | `>` | | |
| Append | | `>>` | | |
| Pipe | | &#124; | | |
| Error | | `2>` | | |
| Exit status | | `$?` | | |
| Quotes | | `"my note.txt"` | | |
| Case | | `Note.txt` | | |

Then answer:

1. What is the difference between standard output and standard error?
2. What does `>` do to an existing file?
3. What does `>>` do?
4. What does a pipe do?
5. What does exit status `0` usually mean?
6. Why are quotes useful for a file name with spaces?
7. Why is `rm *.txt` dangerous?
8. What does `Ctrl` + `C` do?

## What Success Looks Like

You are ready to continue when you can show:

- a disposable `cli-practice` folder;
- a file created with `>`, appended with `>>`, and read with `cat`;
- a pipe that connects two commands;
- an error redirected with `2>`;
- an exit status check;
- one example of quotes, one wildcard listing, and one case-sensitivity error;
- a cleanup that removes only your practice files.

This activity has **no flag**. Your evidence is your notes and your verified
output.

## Key Takeaways

- A command has an executable, optional options, and optional arguments.
- Standard output and standard error are different streams.
- `>` replaces; `>>` appends; `2>` redirects errors.
- A pipe sends one command's output into another command.
- `0` usually means success; nonzero usually means failure.
- Quotes keep a name with spaces together.
- Linux names are case-sensitive.
- Use `Ctrl` + `C` to cancel a line.
- Never combine a wildcard with `rm`.

Next: [Files, Permissions, and Ownership](03_Files_Permissions_and_Ownership.md).
