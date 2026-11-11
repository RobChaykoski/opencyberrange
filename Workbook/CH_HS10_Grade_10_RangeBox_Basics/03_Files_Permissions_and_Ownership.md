# Files, Permissions, and Ownership

This activity uses a disposable folder inside RangeBox. You will view
permissions, predict access, change permissions only on your own practice files,
and restore the original state.

It does **not** use a network target. Do not change permissions outside the
practice folder.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Assigned target** | A practice server named in a lab. | **None. This activity is local to RangeBox.** |

### What you need

- [ ] The RangeBox terminal open.
- [ ] The skills from [Command Line Fluency](02_Command_Line_Fluency.md).
- [ ] A notes file for predictions and results.
- [ ] About **25–35 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain owner, group, other, read, write, execute, and directory traversal;
- read a permission string and a numeric mode;
- tell viewing permissions from changing them;
- predict access before you test it;
- explain why execute means something different for a file and a directory;
- restore the original permissions and remove your practice folder.

## Words to Know

| Term | What it means |
|---|---|
| **Owner** | The user who owns a file or folder. |
| **Group** | A named set of users. The group can be given its own permissions. |
| **Other** | Everyone who is not the owner and not in the group. |
| **Read (`r`)** | For a file, view its contents. For a folder, list the names inside it. |
| **Write (`w`)** | For a file, change its contents. For a folder, create, rename, or remove entries inside it. |
| **Execute (`x`)** | For a file, run it as a program. For a folder, enter or traverse it. |
| **Directory traversal** | The ability to pass through a folder to reach something inside it. It requires execute permission on the folder. |
| **Permission string** | The ten-character code from `ls -l`, such as `-rw-------`. |
| **Numeric mode** | A three-digit code such as `600`, made from read = 4, write = 2, execute = 1. |

## Reading a Permission String

Run `ls -l` and look at the first column:

```text
-rw-------  1 kali kali  42 Nov 11 10:00 note.txt
```

Read it in four parts:

```text
-  rw-  ---  ---
│   │    │    │
│   │    │    └─ other
│   │    └────── group
│   └─────────── owner
└─────────────── file type: - means file, d means directory
```

Each triple has three positions:

| Position | Letter | Meaning | Number |
|---|---|---|---|
| First | `r` | Read | 4 |
| Second | `w` | Write | 2 |
| Third | `x` | Execute | 1 |

Add the numbers for each triple:

| Mode | Owner | Group | Other |
|---|---|---|---|
| `600` | read + write = 6 | none = 0 | none = 0 |
| `644` | read + write = 6 | read = 4 | read = 4 |
| `700` | read + write + execute = 7 | none = 0 | none = 0 |
| `755` | read + write + execute = 7 | read + execute = 5 | read + execute = 5 |

**Viewing is not changing.** `ls -l` shows permissions. `chmod` changes them.
`chmod` does not change the file contents.

## Walkthrough

### Step 1: Create the practice folder

```bash
cd ~
mkdir -p permission-practice
cd permission-practice
pwd
```

**Expected result:** `/home/kali/permission-practice`, or the same path under
your home folder.

**If `cd` fails:** run `pwd` and `ls`, then repeat `mkdir -p permission-practice`
and `cd permission-practice`.

### Step 2: Create disposable content

```bash
echo "permission practice" > note.txt
mkdir folder
echo '#!/bin/sh' > hello.sh
echo 'echo hello from the script' >> hello.sh
ls -l
```

**Why:** you need one file, one folder, and one small script to compare
permissions.

**Expected result:** three entries. The first column of each starts with `-`
for files or `d` for the folder.

### Step 3: Predict before you test

Before you run the next command, write your prediction:

- Can the owner read `note.txt`?
- Can the owner execute `hello.sh`?
- Can the owner enter `folder`?

Now test the first one:

```bash
cat note.txt
```

**Expected result:** `permission practice`.

If the owner can read it, the `r` bit is set for the owner.

### Step 4: View the folder permissions

```bash
ls -ld folder
```

**Why:** `-d` asks about the folder itself, not its contents. `-l` asks for the
long view.

**Expected result:** a line starting with `d`, such as:

```text
drwxr-xr-x  2 kali kali 4096 Nov 11 10:05 folder
```

Read the owner, group, and other triples. The owner usually has `rwx`: list,
create, and enter.

### Step 5: Change one file to owner-only

**Predict:** after this change, can the owner still read the file?

```bash
chmod 600 note.txt
ls -l note.txt
cat note.txt
```

**Why:** `600` gives the owner read and write, and no permissions to group or
other. The owner should still read it.

**Expected result:** `-rw-------` and the text `permission practice`.

### Step 6: Remove owner read and write

**Predict:** what will `cat` do now?

```bash
chmod 000 note.txt
ls -l note.txt
cat note.txt
```

**Why:** `000` removes read, write, and execute from everyone. As the owner, you
should no longer be able to read the file.

**Expected result:** `----------` and a message such as `Permission denied`.

**Important:** you can still change the permissions back because you own the
file. Do that now:

```bash
chmod 600 note.txt
cat note.txt
```

**Expected result:** the text is readable again.

### Step 7: Test execute on a file

**Predict:** can the owner run `hello.sh` before the execute bit is set?

```bash
ls -l hello.sh
./hello.sh
```

**Why:** `./` means "run this file from the current folder". Without execute
permission, the shell should refuse.

**Expected result:** `Permission denied`.

Now add execute for the owner and try again:

```bash
chmod 700 hello.sh
ls -l hello.sh
./hello.sh
```

**Expected result:** `-rwx------` and `hello from the script`.

**What to notice:** execute on a **file** means the operating system may run it
as a program. It does not mean the file is safe.

### Step 8: Test execute on a folder

**Predict:** can you enter `folder` if the owner has read and write but not
execute?

```bash
chmod 600 folder
ls -ld folder
cd folder
```

**Why:** execute on a **folder** means traverse or enter. Without it, `cd` should
fail even though the owner can read the folder's name.

**Expected result:** `drw-------` and `Permission denied`.

Return to the practice folder and restore the folder:

```bash
cd ..
chmod 700 folder
cd folder
pwd
cd ..
```

**Expected result:** you can enter the folder again.

### Step 9: Explain the difference

Write one sentence for each:

- Execute on a file means…
- Execute on a folder means…

A strong answer says that execute on a file allows the system to run it, while
execute on a folder allows a user to pass through or enter it. Reading a folder
only lists names; it does not let you enter.

### Step 10: Restore and clean up

```bash
pwd
ls -l
chmod 600 note.txt
chmod 700 hello.sh
chmod 700 folder
rm note.txt hello.sh
rmdir folder
cd ..
rmdir permission-practice
```

**Why:** this restores the practice files and removes only the disposable
folder.

**If `rmdir` says the folder is not empty:** run `ls permission-practice` and
remove only files you created. If you are unsure, leave the folder and ask. Do
not use `rm -r`, `rm -rf`, or a wildcard.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong folder | `pwd` is not `permission-practice` | Run `cd ~/permission-practice`. If it is missing, repeat Step 1. |
| Permission denied | `Permission denied` | Check `ls -l`. You may have removed your own access. Restore it with `chmod` as the owner. |
| Cannot enter a folder | `cd: Permission denied` | Check `ls -ld folder`. Add owner execute with `chmod 700 folder`. |
| Script will not run | `Permission denied` | Check whether the owner has `x`; use `chmod 700 hello.sh`. |
| Script runs but prints an error | The script content is wrong | Run `cat hello.sh` and check the two lines. |
| Wrong owner or group | `ls -l` shows a user or group you do not recognise | Stop. Do not use `chown` or `sudo`. Ask your teacher. |
| Unsure what changed | You cannot remember the original mode | Stop. Do not change more permissions. Ask your teacher. |

## Record Your Evidence

| Test | Mode before | Prediction | Command | Result | Mode after |
|---|---|---|---|---|---|
| File read | | | `cat note.txt` | | |
| File no read | | | `cat note.txt` | | |
| Script execute | | | `./hello.sh` | | |
| Folder traverse | | | `cd folder` | | |

Then answer:

1. What does the first character of `ls -l` tell you?
2. What do the next three characters tell you?
3. What does owner, group, and other mean?
4. What number means read, write, and execute?
5. Why does execute mean different things for a file and a folder?
6. What is the difference between viewing and changing permissions?
7. Why did you restore the original mode?
8. Why should you not use `chown` or `sudo` here?

## What Success Looks Like

You are ready to continue when you can show:

- a permission string read correctly;
- a numeric mode explained;
- one prediction that matched and one that surprised you;
- a file read test, a script execute test, and a folder traversal test;
- restored permissions and a clean practice folder;
- a clear explanation of why execute differs for files and folders.

This activity has **no flag**. Your evidence is your notes and your restored
practice folder.

## Key Takeaways

- Permissions describe who can read, write, and execute.
- The permission string has a type character and three triples.
- Numeric mode uses read = 4, write = 2, execute = 1.
- Execute on a file means run it; execute on a folder means enter or traverse it.
- Viewing permissions with `ls -l` is not the same as changing them with `chmod`.
- Change permissions only in your own practice folder, predict first, and restore
  the original state.
- Do not use `chown` or `sudo` in this beginner activity.

Next: [Processes, Services, and Applications](04_Processes_Services_and_Applications.md).
