# Target and Connectivity Check

This extra practice activity is a **preflight check**. Before you run a network
command in a later lab, you will:

1. find the assigned target in the exercise panel;
2. copy it into a labelled note;
3. compare it with the workbook example;
4. make **one read-only request** to confirm that the target answers.

A connectivity check is not a scan, a login, or an exploit. It answers one
question: "Can RangeBox reach this one service?"

## Before You Begin

Complete [Internet and Network Basics](05_Internet_and_Network_Basics.md) first.
You should already know what a hostname, IP address, port, protocol, request, and
response are.

### Where to run this activity

| Place | What it is | Used in this activity? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only to view the OpenCyberRange page. |
| **Web browser** | The app that shows the exercise page and the RangeBox desktop. | Yes. |
| **Exercise panel** | The part of the exercise page that shows the lab status and targets. | **Yes. This is where you find the assigned target.** |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Yes. This is your practice workstation. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run the check here.** |
| **Assigned target** | The practice server named in your exercise. | **Yes. This is the only network system you may contact.** |
| **Public internet** | Real websites and services outside the lab. | **No. It is out of scope.** |

!!! warning "Stop if the target does not match"
    The workbook example for this chapter is `rangebox.lab` on port `8080`.
    If the exercise panel shows a **different hostname or port**, do not run the
    command. Write down both values, stop, and ask your teacher which one is
    correct. Do not guess, do not try both, and do not scan to find out.

### What you need

- [ ] The exercise page open, with the exercise running.
- [ ] The RangeBox terminal open.
- [ ] A notes file with a page or section called **Target Card**.
- [ ] About **10–15 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- find the assigned target in the exercise panel;
- copy the target into a labelled note before using it;
- explain the difference between a connectivity check, a scan, a login, and an
  exploit;
- annotate one safe connectivity command;
- explain success, timeout, unreachable, connection refused, and
  name-resolution failure;
- stop and ask when the displayed target differs from the workbook example.

## Words to Know

Read this table before you start.

| Term | What it means |
|---|---|
| **Target** | The practice server assigned to the activity. It is the only network system you may contact. |
| **Target label** | The human-readable name shown next to a target in the exercise panel, such as "RangeBox practice target". |
| **Hostname** | A human-readable name for a host, such as `rangebox.lab`. |
| **IP address** | The number-based address shown for a host in the exercise panel. It may change when the lab starts. |
| **Port** | The number that identifies which service on the target should receive the request. |
| **Connectivity check** | One read-only request to one known host, port, and path to see whether the service answers. |
| **Scan** | Trying many hosts, ports, or services to discover what is there. A scan is not a connectivity check. |
| **Login** | Sending a username and password, or opening an authenticated session. This activity does not log in. |
| **Exploit** | Trying to make a system behave outside its intended use, or bypass its security. This activity does not exploit anything. |
| **Name resolution** | The process of turning a hostname into an IP address. DNS does this. |
| **DNS** | Domain Name System: the naming system that resolves hostnames to IP addresses. |
| **Timeout** | The command waited for a response and did not get one in time. |
| **Unreachable** | The host could not be reached at all, often because there is no route to it. |
| **Connection refused** | The host was reached, but the service on that port refused the connection. |
| **HEAD request** | An HTTP request that asks for response headers only, not the file body. |
| **Status code** | A number in an HTTP response that summarises the result, such as `200` for success or `404` for not found. |

## Where the Target Appears

Open the exercise page and look at the exercise panel. The platform may show a
**Targets** section with these parts:

| Panel label | What it shows | What you copy |
|---|---|---|
| **Your targets:** | One or more target labels and their IP addresses. | The label and the IP address, exactly as shown. |
| **Target Hostnames** | A hostname and a short description, such as `rangebox.lab` and "RangeBox practice target (HTTP 8080)". | The hostname and the port from the description or the workbook. |
| Note under **Target Hostnames** | Text such as "Lab DNS resolves these names automatically inside RangeBox." | Nothing. It tells you the hostname should work inside RangeBox. |

The workbook example for this chapter is:

```text
rangebox.lab:8080
```

That means:

- hostname: `rangebox.lab`
- port: `8080`

The exercise panel is the source of truth for your lab. The workbook example is
only an example.

### If the panel shows an IP address but no hostname

Do not guess a hostname. Copy the IP address exactly into your Target Card and
ask your teacher to confirm that it is the correct target before you run the
command. Do not use an IP address from another student, a screenshot, or a
website.

### If the target differs from the workbook example

**Stop.** Do not run the command. Write down:

- the target shown in the exercise panel;
- the target in the workbook;
- where you saw each one.

Then ask your teacher which target is correct for your exercise. A mismatch is a
reason to check, not a reason to try both.

## Target Card

Copy this into your notes **before** you run any network command. Fill in every
row you can see.

| Field | Your note |
|---|---|
| Activity name | |
| Where I found the target | Exercise panel / workbook |
| Target label | |
| Hostname | |
| IP address | |
| Port | |
| Path | |
| Workbook example | `rangebox.lab:8080` |
| Do the hostname and port match the workbook example? | Yes / No |
| If No, I stopped and asked | Yes / No |

A **Target Card** is a labelled note that records exactly what you are allowed to
contact. It prevents you from copying the wrong address or using a target from a
different activity.

## Connectivity Check, Scan, Login, or Exploit?

These actions are not the same. Only the first one belongs in this activity.

| Action | What it does | Allowed here? |
|---|---|---|
| **Connectivity check** | Sends one read-only request to one known host, port, and path. | **Yes.** |
| **Scan** | Tries many hosts, ports, or services to discover what exists. | **No.** |
| **Login** | Sends credentials or opens an authenticated session. | **No.** |
| **Exploit** | Tries to bypass security or change how a system behaves. | **No.** |
| **Downloading many files** | Requests file after file from the target. | **No.** |
| **Using a public website** | Contacts the public internet. | **No.** |

A successful connection is **not** permission to do more. Permission comes from
the exercise instructions, not from the fact that a service answered.

## The One Command

This is the only network command in this activity:

```bash
curl -I http://rangebox.lab:8080/welcome.txt
```

Read it one part at a time:

```text
curl -I http://rangebox.lab:8080/welcome.txt
│    │  │      │             │    │
│    │  │      │             │    └─ path: /welcome.txt
│    │  │      │             └────── port: 8080
│    │  │      └──────────────────── hostname: rangebox.lab
│    │  └─────────────────────────── protocol: http
│    └────────────────────────────── option: -I, headers only
└─────────────────────────────────── command: curl
```

| Part | Meaning |
|---|---|
| `curl` | The command that sends the request. |
| `-I` | A capital letter I. Send a **HEAD** request and show response headers only. Do not download the body. |
| `http://` | Use the HTTP protocol. |
| `rangebox.lab` | The hostname from the exercise panel. |
| `:8080` | The port. |
| `/welcome.txt` | The path to the file. |

If your teacher confirms a different target, use this template only with the
exact values from the exercise panel:

```text
curl -I http://TARGET:PORT/PATH
```

Replace `TARGET`, `PORT`, and `PATH` only with values you copied into the Target
Card. Do not guess or try other values.

## Walkthrough

### Step 1: Open the exercise panel

Open your exercise and find the **Targets** section. It may show **Your targets:**
and **Target Hostnames**.

**You should see:** a target label, an IP address, and possibly a hostname such
as `rangebox.lab`.

If you do not see any target, stop and ask your teacher. Do not scan the network
to discover one.

### Step 2: Fill in the Target Card

Copy the target details into your notes.

**You should see:** a completed Target Card with the target label, hostname, IP
address, port, and path.

Do not continue until the card is filled in.

### Step 3: Compare the target with the workbook example

The workbook example is `rangebox.lab:8080`.

Compare the **hostname** and the **port**, not the IP address. The IP address may
change each time the lab starts.

**If the hostname and port match:** continue to Step 4.

**If they do not match:** stop. Do not run the command. Ask your teacher.

### Step 4: Run the connectivity check

In the RangeBox terminal, run:

```bash
curl -I http://rangebox.lab:8080/welcome.txt
```

**You should see:** a response that starts with an HTTP status line, followed by
headers. You should not see the file body, because `-I` asks for headers only.

### Step 5: Read the result

Use this table to decide what happened.

| What you see | What it means | Safe next step |
|---|---|---|
| `HTTP/1.1 200 OK` | Success. The target answered and the path was found. | Continue to Step 6. |
| Another status such as `301`, `403`, `404`, or `500` | The target answered, but the request had a different result. | The connection worked. Check the path or ask your teacher. Do not scan. |
| `curl: (6) Could not resolve host` | Name resolution failed. DNS could not turn the hostname into an IP address. | Check the spelling and the exercise. Ask your teacher. |
| `curl: (7) Failed to connect ... Connection refused` | The host was reached, but the service on that port refused the connection. | Check that the lab is running and the port matches the exercise. Ask your teacher. |
| `curl: (7) ... No route to host` or `Network is unreachable` | The host could not be reached at all. | Check the lab status. Ask your teacher. Do not try other hosts. |
| No output for about 10 seconds | The command is waiting. This is a **timeout** in progress. | Press `Ctrl` + `C` to stop waiting. Check the lab and ask your teacher. |
| `curl: (28)` and a message containing `timed out` | The command waited and then reached a timeout. | Check the lab status and ask your teacher. |
| A real website or search page | You are outside the lab. | Stop. Close that page and return to the exercise. |

**Important:** a response code such as `404` or `403` still means the network
connection worked. A **connection failure** is different from a **content
failure**.

### Step 6: Write one sentence

Write one sentence in your notes that explains the result. For example:

- "The target answered with `200 OK`, so RangeBox can reach the service on port
  8080."
- "The hostname did not resolve, so I stopped and checked the exercise instead of
  trying another address."

This sentence is your evidence. The command alone is not enough.

## What Success Looks Like

You are ready to continue when you can show:

- a completed **Target Card** with the target label, hostname, IP address, port,
  and path;
- a note that says whether the hostname and port match the workbook example;
- the `curl -I` command and its output;
- one sentence explaining whether the check succeeded or failed;
- one example of a failure path and the safe step you would take;
- a clear statement that you did not scan, log in, exploit, or use the public
  internet.

This activity has **no flag**. Your evidence is your Target Card, your command
output, and your explanation.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| No target shown | The exercise panel has no target section | Stop and ask your teacher. Do not scan to discover a target. |
| Target mismatch | The panel shows a different hostname or port | Stop. Write both values down and ask your teacher. Do not try both. |
| Hostname typo | `Could not resolve host` | Compare the spelling and case with the exercise panel. Type it exactly. |
| Lab not ready | `Connection refused` or `Failed to connect` | Wait, check the lab status, and relaunch if needed. Do not try other ports. |
| No response | The command hangs | Wait about 10 seconds, then press `Ctrl` + `C`. Check the lab and ask your teacher. |
| Status is not 200 | `404`, `403`, or `500` | The connection worked. Check the path or ask your teacher. Do not scan. |
| Wrong exercise | The target belongs to another activity | Stop. Return to the correct exercise and fill in a new Target Card. |
| You see a real website | A search page or shopping site | Stop. Close it and return to the exercise. |

## Analysis Questions

1. Where did you find the target in the exercise panel?
2. What did you write in your Target Card?
3. Which part of the target is the hostname, and which part is the port?
4. Why do you compare the hostname and port, but not the IP address, with the
   workbook example?
5. What is the difference between a connectivity check and a scan?
6. Why is a `404` response not a connection failure?
7. What does `Could not resolve host` mean?
8. What does `Connection refused` mean?
9. What should you do if the exercise panel shows a target that differs from the
   workbook example?
10. Why is a successful connection not permission to do more?

## Key Takeaways

- Find the target in the exercise panel before you run a network command.
- Copy the target into a labelled Target Card before use.
- The workbook example is `rangebox.lab:8080`. The exercise panel is the source of
  truth for your lab.
- If the displayed hostname or port differs from the workbook example, stop and
  ask. Do not guess, try both, or scan.
- A connectivity check uses one known host, one port, and one path, and it is
  read-only.
- A scan, a login, and an exploit are different actions. This activity does none
  of them.
- `curl -I` asks for headers only. It does not download the file body.
- A status code means the target answered. A connection error means it did not.
- A successful connection is not permission to do more. The exercise instructions
  define what is allowed.

When you are ready, continue with [RangeBox File Hunt](02_File_Hunt.md).
