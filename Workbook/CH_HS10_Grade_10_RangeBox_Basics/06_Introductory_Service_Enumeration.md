# Introductory Service Enumeration

This is a tightly bounded introduction to **service enumeration**. You will
verify the assigned target, run **one** scan against **one** host and **one**
port, and interpret the result as evidence.

Enumeration is not exploitation. It is not a login attempt. It does not confirm a
vulnerability. It records what a service reports about itself.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run the scan here.** |
| **Assigned target** | `network.lab:8080` for the Network Basics lab. | **Yes. This is the only host and port in scope.** |

Open the **RangeBox Network Basics** exercise. Confirm the target in the exercise
panel. If the hostname or port differs from `network.lab:8080`, **stop and ask**.

### What you need

- [ ] The Network Basics lab running.
- [ ] The RangeBox terminal open.
- [ ] Your Target Card from [RangeBox Review and Preflight](01_RangeBox_Review_and_Preflight.md).
- [ ] A notes file for the evidence table.
- [ ] About **20–30 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- define enumeration and distinguish it from exploitation, authentication, and
  vulnerability confirmation;
- explain one bounded scan command, its options, target, and output;
- verify the target before execution;
- explain open, closed, filtered, timeout, and name-resolution outcomes;
- record port, service, observation, confidence, and next safe step.

## Words to Know

| Term | What it means |
|---|---|
| **Enumeration** | Systematically observing what a service exposes, such as a port and service name. |
| **Exploitation** | Trying to use a weakness to gain access or change behaviour. This activity does not exploit. |
| **Authentication** | Logging in with credentials. This activity does not log in. |
| **Vulnerability confirmation** | Proving that a specific weakness exists. A service name or version alone does not confirm one. |
| **Scan** | Sending requests to discover which ports or services respond. |
| **Open port** | A service accepted a connection on that port. |
| **Closed port** | The host responded, but no service accepted the connection on that port. |
| **Filtered port** | No response arrived; something may be blocking it. This is not proof of a firewall. |
| **Timeout** | The scan waited and did not receive a response in time. |
| **Name resolution** | Turning a hostname into an IP address. |
| **Confidence** | How strongly the evidence supports your statement: low, medium, or high. |

## What Enumeration Is and Is Not

| Action | Is it enumeration? | Why |
|---|---|---|
| Sending one service check to one assigned port | **Yes** | It observes what the service reports. |
| Trying to log in with a username and password | No | That is authentication. |
| Running an exploit | No | That is exploitation. |
| Claiming a service is vulnerable because of its version | No | That is an unsupported conclusion. |
| Scanning a whole subnet or many ports | No | That is broad discovery and is outside this activity. |
| Reading a service banner and recording uncertainty | **Yes** | It records an observation without overclaiming. |

A service being **open** means it accepted a connection. It does not mean the
service is unsafe, unpatched, or authorized for more testing.

## The One Command

```bash
nmap -sV -p 8080 network.lab
```

Read it one part at a time:

| Part | Meaning |
|---|---|
| `nmap` | The scanning program included in the RangeBox image. |
| `-sV` | Try to identify the service and version. |
| `-p 8080` | Scan **only** port 8080. |
| `network.lab` | The assigned hostname from the exercise panel. |

The command scans **one host** and **one port**. Do not add `-p-`, a subnet, a
range of ports, or another hostname.

If your teacher confirms a different target, use only the values from the
exercise panel:

```text
nmap -sV -p PORT TARGET
```

Replace `PORT` and `TARGET` with the exact values in your Target Card. Do not
guess.

## Walkthrough

### Step 1: Verify the target before the scan

- [ ] Open the exercise panel.
- [ ] Confirm the hostname `network.lab` and port `8080`.
- [ ] Confirm the same values in your Target Card.

**Why:** a scan against the wrong target is outside scope.

**If the target differs:** stop. Do not run the scan. Ask your teacher.

### Step 2: Run the bounded scan

```bash
nmap -sV -p 8080 network.lab
```

**Expected result:** output similar to:

```text
Starting Nmap ...
Nmap scan report for network.lab (TARGET_IP)
Host is up.
PORT     STATE SERVICE VERSION
8080/tcp open  http    <service version>
```

The exact version text may differ. Do not copy a version from this page; record
what your scan shows.

**If `nmap` is not found:** use the safe fallback:

```bash
curl -I http://network.lab:8080/status.json
```

The `curl` check still confirms that the service answers, but it does not provide
an `nmap` service label. Record that limitation. Do not install a tool.

### Step 3: Read the output line by line

| Field | What it means | Your note |
|---|---|---|
| `Nmap scan report for network.lab` | The hostname the scan used. | |
| `Host is up` | The host answered. | |
| `PORT` | The port column. | |
| `STATE` | `open`, `closed`, `filtered`, or another state. | |
| `SERVICE` | The service label, such as `http`. | |
| `VERSION` | Extra version text, if `-sV` found it. | |

**Observation:** "Port 8080 is open and the service label is http."

**Interpretation:** "The target is running an HTTP service on the port named in
the exercise."

**What you cannot conclude:** "The service is vulnerable." A service label and
version are not proof of a weakness.

### Step 4: Retrieve the lab flag

The Network Basics lab stores its flag in the `X-OCR-Token` response header. If
you have not submitted it, run:

```bash
curl -s -D - -o /dev/null http://network.lab:8080/status.json | grep -i x-ocr-token
```

Copy the `OCR{...}` value into the exercise panel.

**Why:** the flag confirms that you reached the lab, not that you exploited it.

### Step 5: Explain the possible outcomes

| Outcome | What you may see | Safe interpretation |
|---|---|---|
| **Open** | `8080/tcp open http` | A service accepted a connection. It is not automatically vulnerable. |
| **Closed** | `8080/tcp closed` | The host responded, but no service accepted the connection. |
| **Filtered** | `8080/tcp filtered` | No response arrived. Something may be blocking it. Do not assume a firewall. |
| **Timeout** | The scan waits, then reports a timeout | The scan did not get a response in time. Check the lab status. |
| **Name-resolution failure** | `Failed to resolve "network.lab"` | DNS could not map the name. Check the target and exercise. |

### Step 6: Build the evidence table

| Port | Service | Observation | Confidence | Next safe step |
|---|---|---|---|---|
| 8080 | | | Low / Medium / High | |

**Next safe step** means a safe action inside this activity, such as "record the
result" or "ask the teacher about the target." It does not mean "try an
exploit."

## What Not to Do

- Do not scan any other host.
- Do not scan any other port.
- Do not use a subnet, a range, or `-p-`.
- Do not try to log in or guess credentials.
- Do not run an exploit.
- Do not claim a vulnerability from a service name or version.
- Do not use `sudo` to get a different scan result.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong target | The exercise panel differs from the workbook | Stop and ask. Do not scan. |
| `nmap` missing | `command not found` | Use the `curl -I` fallback. Do not install tools. |
| Permission error | A scan error about privileges | Do not use `sudo`. Use the `curl` fallback or ask. |
| Name resolution failure | `Failed to resolve` | Check spelling and the exercise. Ask. |
| Filtered or timeout | No response | Check the lab status. Do not scan other ports. |
| Closed | `closed` | Record it. Do not assume the host is down. |
| You are unsure what the version means | A version string | Record it as an observation and mark confidence low. Do not claim a vulnerability. |

## Record Your Evidence

| Question | Your answer |
|---|---|
| Target hostname | |
| Target port | |
| Command used | |
| State | |
| Service label | |
| Version text | |
| What I observed | |
| What I interpret | |
| What I cannot conclude | |
| Confidence | Low / Medium / High |
| Next safe step | |

Then answer:

1. What is enumeration?
2. How is enumeration different from exploitation?
3. How is it different from authentication?
4. Why does an open port not prove a vulnerability?
5. What does `-sV` ask `nmap` to do?
6. Why is `-p 8080` safer than scanning every port?
7. What does a filtered result tell you, and what does it not tell you?
8. What would you do if the target in the exercise panel differed from the
   workbook?

## What Success Looks Like

You are ready to continue when you can show:

- a verified target;
- one bounded scan of one host and one port;
- output read line by line;
- an evidence table with port, service, observation, confidence, and next safe
  step;
- a clear statement that the scan did not exploit, log in, or confirm a
  vulnerability;
- the lab flag submitted, if it was not already.

This activity uses the **Network Basics** lab flag. The flag is evidence of
completion, not proof of a vulnerability.

## Key Takeaways

- Enumeration observes what a service exposes. It does not exploit it.
- Scan only the assigned host and port.
- `-sV` asks for service/version information; `-p 8080` limits the scan.
- An open port is not a vulnerability.
- A filtered or timeout result is uncertain evidence.
- Record observation, interpretation, confidence, and the next safe step.
- The flag confirms completion, not exploitation.

Next: [Logs and Event Review](07_Logs_and_Event_Review.md).
