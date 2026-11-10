# Capstone: The Forwarded Message

## Before You Begin

- [ ] You have completed **Read the Link Before You Click**
- [ ] You have completed **Know the File Before You Open It**
- [ ] You have the exercise panel open
- [ ] You can open CyberChef and a terminal
- [ ] You will not click the link or open the attachment directly

!!! note "This is a capstone"
    You are not learning a new tool. You are combining two habits: read the
    link, then check the file. The goal is a decision you can explain, not just
    a flag.

## Scenario

You are helping at a community centre. A volunteer forwards a grant review
notice and asks whether it is safe to open the attachment. The message is
polite, the link looks official, and the file name sounds ordinary.

The notice contains two separate clues:

- the link uses a lookalike host and hides a path in an encoded redirect;
- the file at the end of that path is not the type its name claims.

Either clue alone could be a mistake. Together they are enough to stop and
verify.

## Walkthrough

### Step 1: Read the notice without clicking

In the exercise panel, open:

```text
http://capstone.lab:8080/notice.txt
```

Copy the notice. Do not click the link. The notice also gives you the practice
mirror address:

```text
http://capstone.lab:8080
```

### Step 2: Decode the link

Open CyberChef and add **URL Decode**. Paste the notice into the input.

The link looks like this before decoding:

```text
https://communitycentre.example@grant-portal-secure.example/review?next=%2Ffiles%2Fgrant-pack.png
```

After decoding, the `next` value becomes a path:

```text
/files/grant-pack.png
```

Identify the parts before you continue:

| Part | Value |
|---|---|
| Userinfo (before `@`) | `communitycentre.example` |
| Host (after `@`) | `grant-portal-secure.example` |
| Path | `/review` |
| Decoded `next` | `/files/grant-pack.png` |

The real host is a lookalike. The practice mirror is not that host; it is the
local address your instructor provided. Use only the decoded path on the
mirror.

### Step 3: Request the decoded path

Put the mirror address and the decoded path together:

```bash
curl -O http://capstone.lab:8080/files/grant-pack.png
```

If you are using the lab browser, open:

```text
http://capstone.lab:8080/files/grant-pack.png
```

### Step 4: Check the file before opening it

Run `file` on the download:

```bash
file grant-pack.png
```

It should report a **Zip archive**, even though the name ends in `.png`.

Extract it:

```bash
unzip grant-pack.png
```

If `unzip` is unavailable:

```bash
python3 -m zipfile -e grant-pack.png extracted/
cat extracted/token.txt
```

Read `token.txt` and submit the token inside `OCR{...}`.

### Step 5: Write the decision

Write a short note for the volunteer. Use three lines:

```text
What I saw:
What I checked:
What I recommend:
```

A complete answer names both clues: the lookalike host after the `@`, and the
archive disguised as a PNG. The recommendation should be to verify the grant
through a trusted contact and not open the attachment.

## If You Do Not Have a Terminal

1. Decode the notice with CyberChef **URL Decode**.
2. Open the decoded path on the practice mirror in the lab browser.
3. Save the file.
4. Drag it into CyberChef and add **Detect File Type**, then **Unzip**.
5. Read `token.txt` in the output.

If the browser path is not available, ask your instructor for an assisted
walkthrough. Do not open the file directly.

## What Just Happened?

- The link used the same `@` trick as the first exercise. The text before `@`
  is a username, not the host.
- The redirect parameter hid the attachment path with percent-encoding.
- The attachment used a familiar extension to look like an image. `file` showed
  the real type.
- Two independent clues made the message suspicious. One clue alone might be a
  mistake; together they justified stopping.
- A polished message is not evidence of trust. Verify through a channel you
  already know.

## Decision Checklist

Before you act on an unexpected message:

1. Read the real host, not the display text.
2. Decode hidden paths and redirects.
3. Check the file type before opening an attachment.
4. Verify the request through a second channel.
5. Report the message without forwarding the live link or file.
6. If you are unsure, ask. Stopping is a valid outcome.

## Analysis Questions

**1. Which part of the URL decides where the browser goes?**

**2. What did URL Decode reveal that was hidden before?**

**3. Why is a `.png` file that reports as a ZIP archive suspicious?**

**4. Why are two clues stronger than one?**

**5. What would you say to the volunteer in one sentence?**

**6. Why is "the message looked professional" not evidence that it is real?**

**7. What is one thing you would not do with the attachment?**

## Accessibility

- The exercise is text and commands. You can complete it with a keyboard.
- CyberChef and the lab browser are alternatives to the terminal commands.
- Read the URL one part at a time if it is long. The host is always after the
  `@` and before the first `/`.
- If you use a screen reader, ask for the notice as plain text and read it in
  sections.
