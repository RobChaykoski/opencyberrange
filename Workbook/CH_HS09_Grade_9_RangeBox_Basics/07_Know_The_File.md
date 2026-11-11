# Exercise 1.7: Know the File Before You Open It

## Before You Begin

- [ ] You have the exercise panel open
- [ ] You can open a terminal in RangeBox, or the terminal your instructor provides
- [ ] You know you can use hints at any time
- [ ] You will not double-click or execute an unknown file
- [ ] You will use only the fictional files in this exercise

!!! note "A filename is a label"
    A file ending in `.png` or `.pdf` is not guaranteed to be an image or a
    document. The first bytes of the file are stronger evidence than the name.

## Scenario

You are helping at a community centre's volunteer desk. A coordinator
downloaded four files from a shared event folder. One of them does not open the
way its name suggests, and the coordinator asks you to check the files before
anyone opens them.

Your job is to identify what each file really is, find the disguised archive,
and recover the training token without running anything.

## Walkthrough

### Step 1: Download the files

Open a terminal in RangeBox and make a practice folder:

```bash
mkdir -p ~/file-safety
cd ~/file-safety
```

Download the files from the practice target:

```bash
curl -O http://filesafe.lab:8080/downloads/event-photo.png
curl -O http://filesafe.lab:8080/downloads/budget.pdf
curl -O http://filesafe.lab:8080/downloads/agenda.txt
curl -O http://filesafe.lab:8080/downloads/README.txt
```

If you are using the lab browser, the exercise page has links to the same
files. Save them into one folder before continuing.

### Step 2: Check the real type

Run `file` on the downloads:

```bash
file event-photo.png budget.pdf agenda.txt README.txt
```

The output will look similar to this:

```text
event-photo.png: Zip archive data, at least v2.0 to extract
budget.pdf:      ASCII text
agenda.txt:      ASCII text
README.txt:      ASCII text
```

The `.png` file is reported as a **Zip archive**. The extension is wrong. The
`.pdf` file is plain text.

!!! warning "Do not open it yet"
    `file` only reads the first bytes. It does not open or run the file. Keep
    using `file`, `unzip`, and `cat` for this exercise. Do not double-click an
    unknown file.

### Step 3: Extract the disguised archive

The file is a ZIP archive with a misleading name. Extract it:

```bash
unzip event-photo.png
```

If `unzip` is unavailable, use Python:

```bash
python3 -m zipfile -e event-photo.png extracted/
```

List the extracted files and read the token:

```bash
ls
cat token.txt
```

If you used the Python command, the files are in `extracted/`:

```bash
cat extracted/token.txt
```

### Step 4: Check the decoy

The budget file also contains a token, but it is a **decoy**. Read it to see
why it is not the answer:

```bash
cat budget.pdf
```

The real token is the one inside the archive, in `token.txt`. Submit that value.

### Step 5: Write a safe next step

Write one sentence for the coordinator. It should say what you found and what
they should do next. For example:

> The photo is really a ZIP archive with a misleading extension. Please do not
> open it; report it to the event organiser and ask for a fresh copy through a
> channel you already trust.

## If You Do Not Have a Terminal

You can inspect the file in CyberChef:

1. Download `event-photo.png` from the exercise page.
2. Open CyberChef from the platform menu.
3. Drag the downloaded file into the **Input** area, or use the file input.
4. Add **Detect File Type** to the recipe. It should report a ZIP archive.
5. Add **Unzip** to the recipe and inspect the output for `token.txt`.

If the operation output is hard to read in the browser, ask your instructor for
the terminal path. Do not open the file in an image viewer to "check" it.

## What Just Happened?

- An extension is part of a filename. It is a label, not proof of content.
- A ZIP archive starts with the bytes `PK` (`0x50 0x4B`). `file` reads those
  bytes and reports the real type.
- Renaming a file does not change what is inside it.
- Attackers use double extensions, renamed archives, and familiar icons to make
  a file look harmless.
- A decoy token is a trap for anyone who searches for `OCR{` without checking
  which file they are reading.
- The safe response to an unexpected file is to stop, verify, and report it,
  not to disable a warning and open it.

## Safe File Checklist

1. **Expect it?** Were you waiting for this file from this person?
2. **Check the type.** Does `file` agree with the extension?
3. **Check the source.** Did it arrive through a channel you trust?
4. **Do not execute it.** Open documents in a protected viewer, not by
   double-clicking.
5. **Report it.** Send it to your instructor or IT contact without forwarding it
   to classmates.

## Analysis Questions

**1. Why is a filename extension not proof of a file's real type?**

**2. What do the first two bytes `PK` tell you?**

**3. What is the difference between `file` and opening a file?**

**4. Why could the decoy token be dangerous to a hurried learner?**

**5. What would you do if a file you expected arrived with an unusual
extension?**

**6. Why is "it looks like a photo" not enough evidence that it is safe?**

## Accessibility

- All commands are typed text. You can complete the exercise without a mouse.
- Output is plain text and can be read with a screen reader.
- If you cannot use a terminal, use the CyberChef path above or ask your
  instructor for an assisted walkthrough.
- Take breaks if the output is long. Read one command at a time.
