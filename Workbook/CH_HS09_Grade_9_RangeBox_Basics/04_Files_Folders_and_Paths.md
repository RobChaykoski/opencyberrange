# Files, Folders, and Paths

This extra practice activity teaches you how files and folders are organised
inside RangeBox. You will work only in a disposable sandbox folder, check your
location before every action, and remove everything you create.

## Before You Begin

Complete [Terminal Foundations](03_Terminal_Foundations.md) first. You should
already have the RangeBox terminal open and know how to run a command.

### Where to run this activity

| Place | What it is | Used in this activity? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | No. Do not run these commands in a terminal on your own device. |
| **Web browser** | The app that shows the OpenCyberRange page. | Only to view the page. |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Yes. This is where the terminal lives. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Practice target** | The practice server `rangebox.lab:8080`. | Used **once** to download a disposable text file. |
| **Sandbox folder** | `~/practice-files`, which means `/home/kali/practice-files`. | **Yes. Every file action happens here.** |

This activity uses the same target as [Signing In and Opening RangeBox](01_First_Steps.md).
If your exercise does not include `rangebox.lab:8080`, ask your teacher for the
practice file. Do not download from a real website or a different target.

### What you need

- [ ] The RangeBox terminal open.
- [ ] The practice target `rangebox.lab:8080` available in your exercise.
- [ ] A notes file for your commands and output.
- [ ] About **20–25 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain what a file, folder, path, home folder, and current directory are;
- tell an absolute path from a relative path;
- explain why Linux paths and filenames are case-sensitive;
- create a sandbox folder and a subfolder;
- list, read, move, copy, and remove only disposable practice content;
- check your current directory before every file action;
- verify the result of each action;
- undo a safe action, or recognise when an action cannot be undone.

!!! warning "Only work inside the sandbox"
    Use only `~/practice-files`. Do not delete, move, or rename anything outside
    it. Do not use `rm` with `*`, `rm -r`, `rm -rf`, or `sudo`. Do not create,
    rename, or delete hidden files. If `pwd` does not show
    `/home/kali/practice-files` or `/home/kali/practice-files/notes`, stop and
    ask your teacher before you continue.

## Words to Know

Read this table before you type anything.

| Term | What it means |
|---|---|
| **File** | A named piece of data, such as a text file, picture, or document. |
| **Folder** | A container that holds files or other folders. **Directory** means the same thing. |
| **Path** | The route to a file or folder, written with `/` between folder names. |
| **Home folder** | The folder that belongs to your RangeBox account. Here it is `/home/kali`. The shorthand `~` also means the home folder. |
| **Current directory** | The folder you are working in right now. Also called the working directory. `pwd` prints it. |
| **Parent directory** | The folder one level above the current directory. The shorthand `..` means the parent directory. |
| **Absolute path** | A path that starts at the top of the filesystem with `/`. It works from any folder. Example: `/home/kali/practice-files/welcome.txt`. |
| **Relative path** | A path that starts from your current directory. It does not start with `/`. Example: `notes/welcome.txt` when you are in `practice-files`. |
| **File extension** | The part after the last dot in a file name, such as `.txt`. It suggests the file type, but it does not prove what is inside or that the file is safe. |
| **Sandbox folder** | A disposable folder where you can practise. In this activity it is `~/practice-files`. |
| **Hidden file** | A file whose name starts with `.`, such as `.notes`. Hidden files are not shown by a plain `ls`. This activity does not use them. |
| **Wildcard** | The `*` symbol, which can mean "many names". This activity does not use wildcards because they can match more than you expect. |
| **Case-sensitive** | Treating uppercase and lowercase letters as different. Linux paths and file names are case-sensitive, so `welcome.txt` and `Welcome.txt` are different names. |

## Linux Paths Are Not Windows Paths

If you are used to Windows, Linux paths look different. Both can be safe, but
the rules are not the same.

| You may know from Windows | In RangeBox (Linux) |
|---|---|
| `C:\Users\Sam\Documents\notes.txt` | `/home/kali/practice-files/notes.txt` |
| Backslash `\` separates folders. | Forward slash `/` separates folders. |
| A drive letter such as `C:` starts the path. | The root `/` starts the path. There is no `C:` drive. |
| `notes.txt` and `Notes.txt` are usually the same file. | `notes.txt` and `Notes.txt` are **different** files. |
| The current folder is often shown in a window. | `pwd` prints the current folder. |

Examples with the sandbox:

| Path | What it means |
|---|---|
| `/home/kali/practice-files` | The absolute path of the sandbox. |
| `~/practice-files` | The same sandbox, using `~` for `/home/kali`. |
| `practice-files` | A relative path. It works only when your current directory is `/home/kali`. |
| `notes` | A relative path. It works only when your current directory is `/home/kali/practice-files`. |
| `notes/welcome.txt` | A relative path from `practice-files` into the `notes` subfolder. |
| `..` | The parent directory. From `notes`, `..` is `practice-files`. |
| `.` | The current directory. |

## The Safe Pattern

Use the same four checks before and after every file action:

1. **Check:** run `pwd` and confirm you are in `~/practice-files` or
   `~/practice-files/notes`.
2. **Look:** run `ls` and see what is already there.
3. **Act:** run one command only.
4. **Verify:** run `ls` again and read the result.

If the path is not what you expect, **stop**. Run `cd ~/practice-files` to
return to the sandbox, or ask your teacher. Do not continue with a file action
in the wrong folder.

## Walkthrough

Every step shows the current directory and what you should see. Run one command
at a time.

### Step 1: Start in your home folder

**Current directory:** unknown until you check.

Run:

```bash
cd ~
pwd
```

**You should see:** `/home/kali`.

`cd` means "change directory". `~` means your home folder. If you see a
different path, stop and ask your teacher.

### Step 2: Create the sandbox folder

**Current directory:** `/home/kali`

Run:

```bash
mkdir -p practice-files
```

**Verify:** run `ls`.

**You should see:** `practice-files` in the list.

`mkdir` makes a folder. The option `-p` means "create the folder if it is
missing, and do not treat an existing folder as an error". If `practice-files`
already exists, that is fine.

### Step 3: Enter the sandbox

**Current directory:** `/home/kali`

Run:

```bash
cd practice-files
pwd
```

**You should see:** `/home/kali/practice-files`.

From now on, every file action happens here.

### Step 4: Download one disposable practice file

**Current directory:** `/home/kali/practice-files`

Run:

```bash
curl -O http://rangebox.lab:8080/welcome.txt
```

**Verify:** run `ls`.

**You should see:** `welcome.txt`.

`curl` requests a file from the practice target. The option `-O` (capital letter
O) means "save the file using its remote name". If `welcome.txt` already exists,
`curl -O` replaces it. That is acceptable only inside this sandbox.

If the command says it could not resolve the host, or the connection fails, stop.
Check with your teacher that you are in an exercise that includes
`rangebox.lab:8080`. Do not try a different website.

### Step 5: Read the file

**Current directory:** `/home/kali/practice-files`

Run:

```bash
cat welcome.txt
```

**You should see:** the text inside the welcome file. It may include the training
token from the first activity. You do not need to submit it again; this activity
has no flag.

`cat` prints the contents of a text file. `welcome.txt` is an **argument**: it
tells `cat` which file to read.

### Step 6: Create a subfolder

**Current directory:** `/home/kali/practice-files`

Run:

```bash
mkdir notes
```

**Verify:** run `ls`.

**You should see:** `notes` and `welcome.txt`.

### Step 7: Make a backup copy

**Current directory:** `/home/kali/practice-files`

Run:

```bash
cp welcome.txt notes/welcome-backup.txt
```

**Verify:** run `ls notes`.

**You should see:** `welcome-backup.txt`.

`cp` means "copy". The first argument is the source. The second argument is the
destination. Here the destination is a **relative path** inside `notes`.

### Step 8: Move the original file into the subfolder

**Current directory:** `/home/kali/practice-files`

Run:

```bash
mv welcome.txt notes/welcome.txt
```

**Verify:** run `ls` and then `ls notes`.

**You should see:** `ls` no longer lists `welcome.txt` in the sandbox, and
`ls notes` lists `welcome.txt` and `welcome-backup.txt`.

`mv` means "move". It can also rename a file when the destination is in the same
folder. Check the destination with `ls` before you use `mv`; `mv` can replace an
existing file without asking.

### Step 9: Read the moved file

**Current directory:** `/home/kali/practice-files`

Run:

```bash
cat notes/welcome.txt
```

**You should see:** the same text as before.

The relative path `notes/welcome.txt` means "start in the current directory,
enter `notes`, and read `welcome.txt`". You could also use the absolute path
`/home/kali/practice-files/notes/welcome.txt`.

### Step 10: Remove the moved file

**Current directory:** `/home/kali/practice-files`

Run:

```bash
rm notes/welcome.txt
```

**Verify:** run `ls notes`.

**You should see:** only `welcome-backup.txt`.

`rm` removes a file immediately. There is no Recycle Bin in the terminal. Only
remove the exact file you created in this activity, after checking `pwd` and
`ls`. Never use `rm` with `*`, `rm -r`, or `rm -rf`.

### Step 11: Move the backup back

**Current directory:** `/home/kali/practice-files`

Run:

```bash
mv notes/welcome-backup.txt welcome.txt
```

**Verify:** run `ls` and then `ls notes`.

**You should see:** `welcome.txt` in the sandbox, and `notes` is empty.

This is also your undo step for the move: `mv` can put a file back where it was.

### Step 12: Remove the practice file

**Current directory:** `/home/kali/practice-files`

Run:

```bash
rm welcome.txt
```

**Verify:** run `ls`.

**You should see:** only `notes`. The file is gone. If you need it again, you can
download it again with the same `curl -O` command.

### Step 13: Remove the empty subfolder

**Current directory:** `/home/kali/practice-files`

Run:

```bash
rmdir notes
```

**Verify:** run `ls`.

**You should see:** no files or folders listed.

`rmdir` removes an **empty** folder. If it says the directory is not empty, run
`ls notes` and remove only your own practice files. Do not use `rm -r`.

### Step 14: Leave the sandbox

**Current directory:** `/home/kali/practice-files`

Run:

```bash
cd ..
pwd
```

**You should see:** `/home/kali`.

`..` means the parent directory. This is the undo step for entering the sandbox.

### Step 15: Remove the empty sandbox

**Current directory:** `/home/kali`

Run:

```bash
rmdir practice-files
```

**Verify:** run `ls`.

**You should see:** no `practice-files` entry.

If the folder is not empty, do not force it. Run `ls practice-files`, check what
is there, and remove only your own practice content. Ask your teacher if you are
unsure.

## Undo and Recovery

| Action | Safe undo | What to know |
|---|---|---|
| `cd ~` or `cd practice-files` | `cd ..` or `cd ~` | Changing folder does not change files. |
| `mkdir -p practice-files` | `rmdir practice-files` | Only works when the folder is empty. |
| `curl -O ...` | `rm welcome.txt` | Only remove the file you downloaded in the sandbox. |
| `cp welcome.txt notes/welcome-backup.txt` | `rm notes/welcome-backup.txt` | Check the path before removing. |
| `mv welcome.txt notes/welcome.txt` | `mv notes/welcome.txt welcome.txt` | Check both paths before moving. |
| `rm welcome.txt` | No undo | Download it again with the same `curl -O` command. |
| `rmdir notes` | `mkdir notes` | Only works when the folder is empty. |
| A wrong folder | `cd ~/practice-files` | Stop and check `pwd` before any file action. |

If you delete or move the wrong file, **stop**. Do not try to fix it with a broad
command. Tell your teacher what you ran and what you saw. Your notes are the
evidence, so write down the command before you try a recovery step.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong folder | `pwd` shows a path outside `practice-files` | Stop. Run `cd ~/practice-files`. If that fails, ask your teacher. |
| Folder missing | `cd: no such file or directory` | Run `pwd` and `ls`. Create the sandbox again with `mkdir -p practice-files`. Check the spelling and case. |
| Folder already exists | `mkdir: cannot create directory ... File exists` | This is not a problem. Run `cd practice-files` and continue. |
| Download fails | `Could not resolve host` or a connection error | Check that your exercise includes `rangebox.lab:8080`. Ask your teacher. Do not use another website. |
| File not found | `cat: ... No such file or directory` | Run `pwd` and `ls`. Check the spelling, the path, and the capital letters. Linux is case-sensitive. |
| Folder not empty | `rmdir: failed to remove ... Directory not empty` | Run `ls` on that folder. Remove only your own practice files with `rm`, then try `rmdir` again. Never use `rm -r`. |
| Tried to remove a folder with `rm` | `rm: cannot remove ... Is a directory` | Use `rmdir` only if the folder is empty. Do not add `-r`. |
| Permission denied | `Permission denied` | You may be outside your home folder. Stop and ask your teacher. Do not use `sudo`. |
| A file was replaced by `mv` | The destination name already existed | Stop. Check `ls`. Recreate only the practice file you downloaded. Tell your teacher if you are unsure. |
| The terminal seems frozen | No new prompt | Wait. If it still does not return, use **Stop Exercise** and relaunch. Your notes outside the desktop are safe. |

## Record Your Evidence

Copy this table into your notes and fill it in.

| Step | Command | Current directory before the action | What changed | How I verified it |
|---|---|---|---|---|
| Create sandbox | | | | |
| Download file | | | | |
| Read file | | | | |
| Move file | | | | |
| Remove file | | | | |
| Clean up | | | | |

Then answer these questions.

1. What is the difference between an absolute path and a relative path?
2. What does `~` mean, and what does `..` mean?
3. Why did you run `pwd` before every file action?
4. Why are `welcome.txt` and `Welcome.txt` different in RangeBox?
5. What is the file extension of `welcome.txt`, and what does it tell you?
6. Which command removes an empty folder, and which command removes a file?
7. Which action in this activity cannot be undone?
8. What would you do if `pwd` showed `/home/kali` when you expected to be in
   `practice-files`?

## What Success Looks Like

You are ready to continue when you can show:

- a note with `pwd` before and after the sandbox work;
- the output of `ls` after creating, moving, reading, and removing the file;
- a clear explanation of absolute and relative paths;
- a clear explanation of why Linux paths and filenames are case-sensitive;
- one undo step and one action that cannot be undone;
- an empty sandbox removed at the end, with no practice files left behind.

This activity has **no flag**. Your evidence is your notes and your explanation.

## Key Takeaways

- A file holds data; a folder, or directory, holds files and other folders.
- A path is the route to a file or folder. Absolute paths start with `/`;
  relative paths start from the current directory.
- `~` means the home folder, `.` means the current directory, and `..` means the
  parent directory.
- Linux uses `/` between folders, not `\`, and Linux paths and filenames are
  case-sensitive.
- Run `pwd` and `ls` before every file action, and `ls` again to verify.
- Work only in `~/practice-files`. Never use broad deletion, wildcards, or
  `sudo`.
- `rm` has no undo. A backup copy or a second download is the safe recovery.

When you are ready, continue with [RangeBox File Hunt](02_File_Hunt.md).
