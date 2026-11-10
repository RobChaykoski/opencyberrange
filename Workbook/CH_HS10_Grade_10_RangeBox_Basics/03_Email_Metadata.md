# Dissect an Email

## Before You Begin

- [ ] You have the exercise panel open
- [ ] You can open a terminal in RangeBox, or the terminal your instructor provides
- [ ] You know you can use hints at any time
- [ ] You will not click any link in the message
- [ ] You will use only the fictional message in this exercise

!!! note "Read the raw message, not the mail view"
    A mail app shows the friendly parts: sender name, subject, and body. The raw
    message also contains the envelope sender, routing hops, authentication
    results, and custom headers. Those are the parts an investigator reads
    first.

## Scenario

A volunteer at a community centre forwards a grant review email and asks
whether it is real. The message looks ordinary in the mail app. You have the
raw `.eml` file, which preserves every header the mail servers added.

Your job is to read the message as data, decide what the headers support, and
recover the training token from the case metadata. The token is not in the
body.

## Walkthrough

### Step 1: Download the raw message

In a terminal:

```bash
mkdir -p ~/email-lab
cd ~/email-lab
curl -O http://emailmeta.lab:8080/email.eml
ls -l
```

If you are using the lab browser, the exercise page has a **Download
reported-email.eml** button. Save it and open it in a text editor.

### Step 2: Separate the headers from the body

Open the file as text:

```bash
less email.eml
```

The headers are above the first blank line. The body is below it. Most mail
clients hide the headers; a text editor shows all of them.

### Step 3: Compare the sender headers

Look for these headers first:

| Header | What it tells you |
|---|---|
| `From` | What the mail app displays as the sender. It can be spoofed. |
| `Return-Path` | The envelope sender, where bounces go. Added during delivery. |
| `Reply-To` | Where a reply would go. It can differ from `From`. |
| `Message-ID` | A unique identifier created by the sending system. |
| `Date` | The sender's clock and timezone. |

Ask: do `From`, `Return-Path`, and `Reply-To` describe the same organisation?
If one uses a different domain, that is a reason to slow down.

### Step 4: Read the Received chain

An email passes through mail servers. Each server adds a `Received` header at
the **top** of the message. That means the headers are in reverse order: the
top one is the last hop, and the bottom one is the earliest hop.

```text
Received: from mx.communitycentre.example ...        (last hop)
Received: from smtp.mailer-relay.example ...
Received: from grant-portal-secure.example ...       (first hop)
```

Read from the bottom up. The bottom `Received` header names the system that
first accepted the message and often includes its IP address. Compare that name
with the organisation the message claims to be from. A relay you do not
recognise is a clue, not proof.

### Step 5: Read the authentication results

Find `Authentication-Results` and `Received-SPF`. Three checks matter:

| Check | Question it answers |
|---|---|
| **SPF** | Did this IP address have permission to send mail for the envelope domain? |
| **DKIM** | Is there a valid cryptographic signature from the signing domain? |
| **DMARC** | Do SPF or DKIM align with the `From` domain, and what should the receiver do on failure? |

A `fail` or `none` result is evidence to investigate. It is not proof by itself:
legitimate mail can fail after forwarding, and attackers can sometimes pass one
check while failing another. Combine the result with the sender mismatch and
the routing chain.

### Step 6: Look for custom metadata

Headers beginning with `X-` are added by mail systems, applications, or
senders. They often carry routing tags, case identifiers, or software details.
Useful examples in this message include:

- `X-Originating-IP`
- `X-Mailer`
- `X-Spam-Status`
- `X-OCR-Case-Token`

Read the case token header and copy the value inside `OCR{...}` into the flag
box. The `Reference:` line in the body is a decoy, not the case token.

### Step 7: Write the verdict

Write three lines for the volunteer:

```text
What the message claims:
What the headers show:
What I recommend:
```

A complete answer names at least one header, such as the `From`/`Return-Path`
mismatch, the failed SPF result, or the unrecognised originating host.

## If You Do Not Have a Terminal

Use the lab browser to download `reported-email.eml`, then open it in any text
editor available in the desktop. If the file opens in a mail client, use
**Save as** or **View source** to get the raw headers. You can also use
CyberChef with the file as input; the headers are plain text at the top.

## What Just Happened?

- An email has two layers: the **envelope** used by mail servers and the
  **display headers** shown by the mail app. They can disagree.
- `Received` headers are added at the top, so you read the chain from the bottom
  up to find the first hop.
- SPF, DKIM, and DMARC are independent checks. A failure is evidence, not a
  complete verdict.
- `X-` headers are metadata. They can reveal software, routing, case IDs, and
  internal identifiers that the body never shows.
- The body can contain a decoy. The headers are often the better evidence.
- Preserve the raw message before deleting or forwarding it. A screenshot is
  not enough for an investigation.

## Header Map

| Header | Meaning |
|---|---|
| `Return-Path` | Envelope sender; where bounces are sent. |
| `From` | Display sender; what the recipient sees. |
| `Reply-To` | Address used when the recipient replies. |
| `Received` | One routing hop per server; newest at the top. |
| `Authentication-Results` | The receiving server's SPF, DKIM, and DMARC verdicts. |
| `Received-SPF` | Detailed SPF result and the checked IP. |
| `Message-ID` | Unique message identifier; the domain can be a clue. |
| `Date` | Sender's clock and timezone. |
| `X-Originating-IP` | Sender IP recorded by the mail system. |
| `X-Mailer` | Software that created or sent the message. |
| `X-Spam-Status` | Local spam score and tests. |
| `X-OCR-Case-Token` | Training case metadata for this exercise. |

## Analysis Questions

**1. Why can the `From` header disagree with the envelope sender?**

**2. Which `Received` header is the earliest hop, and why?**

**3. What does SPF check? What does DKIM check?**

**4. Why is a failed authentication result not proof that a message is fake?**

**5. What can an `X-` header reveal that the body does not?**

**6. Why should you preserve the raw message instead of taking a screenshot?**

**7. What is one safe next step after reading these headers?**

## Accessibility

- The message is plain text. You can read it with a screen reader or a text
  editor.
- All terminal steps are typed text; no mouse is required.
- Header lines can be long. Read one header at a time, and use search for a
  header name if the editor supports it.
- If the raw file is difficult to navigate, ask for a plain-text copy with one
  header per line.
