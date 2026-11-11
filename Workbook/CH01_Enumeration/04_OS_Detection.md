# Exercise 1.4: OS Detection

## Before You Begin

In Exercise 1.3, you used version detection to collect software and version
evidence. This exercise moves one layer down: what operating system is the host
likely running?

Nmap's OS detection does **not** ask the target what it is running. It infers
from how the target's network stack behaves. That makes the result useful
evidence, but it is not a direct observation of the operating system and it is
not guaranteed to be exact.

### Where the commands run

Run every command inside the **RangeBox** terminal (the browser-based lab
desktop) or your own **VPN** (Virtual Private Network)-connected Kali Linux VM.
Do not run them in the OpenCyberRange web page, on the platform server, or on the
target itself.

### What you need

- [ ] The Chapter 1 Introduction and Exercises 1.1–1.3 completed.
- [ ] The lab started and its status shown as **Running**.
- [ ] The target IP copied from the **Active Lab View** or **Exercise Network**
      panel.
- [ ] A terminal in the RangeBox or your VPN-connected Kali VM.
- [ ] A notes file for observations, confidence, and conclusions.

### Estimated time

About **20–30 minutes**. OS detection may take longer than a basic scan because
Nmap sends additional fingerprinting probes. Interpretation is part of the work.

### Scope

!!! warning "Authorized target only"
    Scan only the target IP shown in this exercise. Do not scan the platform,
    your RangeBox, other students, your school or employer network, or the
    internet. If the panel does not show a target, stop and ask your instructor;
    do not scan addresses at random.

### What you will be able to do

By the end of this exercise, you will be able to:

- explain OS fingerprinting as inference from network behaviour;
- define observation, fingerprint, confidence, and conclusion;
- explain why `sudo` is used for `nmap -O` and what that privilege means;
- run OS detection against the assigned target;
- interpret a single match, multiple guesses, and “no exact OS match”;
- record uncertainty honestly instead of treating a guess as fact;
- retrieve and submit the flag.

## Scenario

Your reconnaissance of FinanceCorp is progressing. You have discovered open
ports and identified service versions. Now you need evidence about the operating
system. Knowing the likely platform helps you decide which research paths,
administration tools, privilege-escalation techniques, and post-exploitation
tools are relevant. It does not prove that any particular exploit will work.

## Your Objectives

- Use Nmap OS detection (`-O`) to collect operating-system evidence.
- Record the observation, fingerprint evidence, confidence, and conclusion
  separately.
- Interpret a single guess, multiple guesses, and the absence of an exact match.
- Explain the privilege requirement and its security implications.
- Retrieve and submit the flag.

## Background: OS Fingerprinting Is Inference

Different operating systems implement TCP/IP slightly differently. They use
different default **TTL** (Time To Live, a hop limit), **TCP window sizes**
(flow-control values), **DF** (Don't Fragment) behaviour, and **TCP options**
(optional header fields) ordering. Nmap sends crafted probes, observes the
responses, and compares the resulting pattern — the **fingerprint** (the pattern
of responses) — with a database of known fingerprints.

```mermaid
graph LR
    A["Probes sent"] --> B["Responses observed"]
    B --> C["Fingerprint compared<br/>with database"]
    C --> D["One or more<br/>candidate matches"]
    D --> E["Conclusion with<br/>uncertainty"]

    style A fill:#4a90d9,color:#fff
    style B fill:#888,color:#fff
    style C fill:#d9a34a,color:#fff
    style D fill:#5bc0de,color:#fff
    style E fill:#6aaa64,color:#fff
```

This is **inference**, not direct access. Nmap never reads the target's kernel
version, registry, or system files. A firewall, a proxy, a virtual machine, or a
custom network stack can change the responses and shift the fingerprint.

### Terms to keep separate

| Term | Meaning | Example |
|---|---|---|
| **OS family** | A broad platform group. | Windows, Linux, Unix |
| **OS version** | A specific release within a family, when Nmap can infer one. | Windows Server 2019 |
| **Fingerprint** | The pattern of network responses Nmap compares with its database. | TTL, window size, DF behaviour, TCP option ordering |
| **Observation** | A factual record of what Nmap printed. | “Nmap printed `Running: Microsoft Windows 2019`.” |
| **Confidence** | Nmap's match score or guess strength, when it prints one. It is not a guarantee and not a probability that the OS is exactly that version. | A percentage beside an aggressive guess |
| **Conclusion** | Your interpretation of the evidence, with uncertainty stated. | “The target behaves like Windows Server 2019; the lab may be emulating it, so treat this as a guess.” |
| **CPE** | Common Platform Enumeration: a standardized identifier for a platform or product, useful for research. | `cpe:/o:microsoft:windows_server_2019` |
| **Network distance** | The number of hops between the scanner and the target. | `1 hop` |
| **Aggressive guess** | A lower-confidence OS candidate Nmap lists when it cannot make an exact match. | “Aggressive OS guesses” in the output |
| **Sudo** | A command that runs another command with elevated privileges, usually as the administrative `root` user. | `sudo nmap -O <target_ip>` |
| **Privilege** | The level of access a user or process has. Elevated privilege means more power to read or change the system. | Root can change networking configuration |

### Why OS detection uses sudo

The source command for this exercise is:

```bash
sudo nmap -O <target_ip>
```

- `-O` enables OS detection. Nmap sends fingerprinting probes and compares the
  responses with its fingerprint database.
- `sudo` runs the command with elevated privileges because OS fingerprinting
  sends **raw packets** — hand-crafted packets that bypass the normal networking
  stack. Creating raw packets requires low-level access to the network interface.
- Version detection (`-sV`) uses normal TCP connections that an unprivileged
  user can create. OS detection needs deeper access, so the source requests
  `sudo`.

The security implication is real: `sudo` can run a command as `root`, which can
change the system. Run the exact command you intend to run, review it before
pressing Enter, and do not leave a root shell open or use `sudo` for unrelated
commands. If the `sudo` prompt asks for a password you do not have, stop and ask
your instructor. Do not try to bypass the requirement.

### What the result can look like

Nmap's OS detection is probabilistic (it produces a best guess, not a certainty).
A scan may produce:

- **One strong candidate:** an `OS details` line and a CPE identifier.
- **Several candidates:** multiple guesses, often with different confidence
  values. This is a sign to report the ambiguity, not to pick the first one.
- **No exact OS match:** Nmap may say that it has no exact match and then offer
  aggressive guesses, or it may provide very little OS information at all.

A percentage is a **fingerprint-match score**, not a promise. A high score can
still be wrong under virtualization, emulation, firewalls, or unusual network
stacks. A missing percentage is not a failure; it means the evidence is
incomplete.

!!! warning "Do not promise an exact match"
    OS detection is not a direct read of the target. Report the exact wording
    Nmap produced, any confidence values, and the uncertainty. Do not invent a
    version or present a guess as a confirmed fact.

### Source-grounded success example

!!! note "Representative output, not your output"
    This example is from the reference setup. Your target, Nmap version, and
    results may differ. Nmap may not print a confidence value, may print several
    guesses, or may report no exact match. Record what your scan actually prints.

```text
Nmap scan report for 10.100.13.10
PORT    STATE SERVICE
139/tcp open  netbios-ssn
445/tcp open  microsoft-ds

Device type: general purpose
Running: Microsoft Windows 2019
OS details: Microsoft Windows Server 2019
OS CPE: cpe:/o:microsoft:windows_server_2019
Network Distance: 1 hop
```

Annotated reading:

| Field | Example value | What it is | How to record it |
|---|---|---|---|
| Device type | `general purpose` | Nmap's broad device classification. | Observation |
| Running | `Microsoft Windows 2019` | A candidate OS family and version. | Tentative conclusion |
| OS details | `Microsoft Windows Server 2019` | Nmap's best guess at the platform. | Tentative conclusion |
| OS CPE | `cpe:/o:microsoft:windows_server_2019` | A standardized identifier for research. | Observation |
| Network Distance | `1 hop` | The scanner is on the same local network segment. | Observation |
| Confidence | not shown in this example | A match score, if Nmap prints one. | Observation, or “not shown” |

### Source-grounded ambiguous example

This exercise intentionally runs Linux with Samba configured to simulate a
Windows environment. Nmap may report Linux or Windows depending on the
configuration. The ambiguity is realistic: virtualization, service emulation,
and firewalls can make OS detection uncertain.

For an ambiguous result, a good record looks like this:

| Field | Example record |
|---|---|
| Observation | “Nmap printed a Windows Server 2019 candidate and a Linux candidate in its guesses.” |
| Fingerprint evidence | The CPE or fingerprint details Nmap printed for each candidate. |
| Confidence | The percentage beside each guess, or “not shown.” |
| Conclusion | “The target's behaviour is consistent with more than one platform. The lab deliberately emulates Windows on Linux, so I cannot claim an exact OS from this scan alone.” |

Do not choose the candidate that “looks right.” Report what Nmap printed and
state the ambiguity.

## Tool Primer: `sudo nmap -O`

!!! kali "Run OS detection with elevated privileges"
    ```bash
    sudo nmap -O <target_ip>
    ```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Privilege command | `sudo` | Literal | Run the following command with elevated privileges. |
| Executable | `nmap` | Literal | The Nmap program. |
| Option | `-O` | Literal | Enable OS detection. |
| Target | `<target_ip>` | Replace | The IP from your exercise panel. |

**Optional OS-detection options**

- `--osscan-guess`: guess more aggressively when the fingerprint does not
  exactly match a known signature. The guesses are still guesses.
- `--osscan-limit`: skip OS detection on hosts without at least one open and one
  closed TCP port. Nmap needs both kinds of response to fingerprint reliably.

These options change how Nmap handles uncertainty. They do not turn a guess into
a confirmed fact. This exercise uses the source command above; do not add options
unless the walkthrough or your instructor asks you to.

## Walkthrough

### Step 1: Launch the exercise

1. Navigate to **Exercises** and locate the **OS Detection** lab.
2. Click **Launch** and wait for the status to change to **Running**.
3. Copy the **target IP** from the **Active Lab View** or **Exercise Network**
   panel into your notes.

Every command uses the placeholder `<target_ip>`. Replace it with the target IP
from your exercise panel. Do not copy an example IP from the introduction or
another student's screen.

### Step 2: Verify sudo access

!!! kali "Verify sudo access"
    ```bash
    sudo whoami
    ```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Privilege command | `sudo` | Literal | Run the following command with elevated privileges. |
| Executable | `whoami` | Literal | Print the current effective username. |

If the command prints `root`, the privilege path works. If it fails with a
permissions error or asks for a password you do not have, stop and ask your
instructor. Do not attempt to bypass the requirement.

### Step 3: Run OS detection

!!! kali "Run the OS detection scan"
    ```bash
    sudo nmap -O <target_ip>
    ```

    Replace `<target_ip>` with the IP from your exercise panel. The scan takes
    slightly longer than a basic port scan because Nmap sends additional
    fingerprinting probes.

**What success looks like**

- The scan completes and prints OS-related fields.
- You have at least one observation to record: `Running`, `OS details`, `OS
  CPE`, multiple guesses, or an explicit “no exact match” result.
- You can state which part is an observation and which part is a conclusion.
- You can state whether the result is a single candidate, multiple candidates,
  or no exact match.

**Normal uncertainty**

- Nmap may print one candidate, several candidates, or no exact match.
- A confidence value may be absent.
- The candidate may say Linux even when the lab scenario looks Windows-like,
  because the exercise uses Samba to emulate Windows on Linux.
- A firewall or virtualized network may limit the responses Nmap can use.

### Step 4: Interpret the result

Record the output in a table like this. Keep the observation factual and put
your interpretation in the conclusion column.

> **My OS detection record**
>
> | Field | Observation (what Nmap printed) | Fingerprint evidence | Confidence | Tentative conclusion |
> |---|---|---|---|---|
> | Device type |  |  |  |  |
> | Running |  |  |  |  |
> | OS details |  |  |  |  |
> | OS CPE |  |  |  |  |
> | Network distance |  |  |  |  |
> | Other guesses |  |  |  |  |
>
> **Uncertainty statement:** “The scan is consistent with ______, but I cannot
> claim an exact OS because ______.”

Use these rules when reading the result:

- **One candidate:** record it as a tentative conclusion, not a fact.
- **Several candidates:** record all of them and their confidence values. State
  that the evidence does not distinguish between them.
- **No exact match:** record that Nmap did not produce an exact match. If it
  offers aggressive guesses, record them as guesses. This is a valid result, not
  a failed lab.
- **No confidence value:** write “not shown.” Do not invent a percentage.

### Step 5: Find the flag

The target advertises the flag inside its SMB server string. List the shares
with `smbclient` and no password; the server string (the descriptive text the
SMB server advertises) appears in the `IPC$` (inter-process communication share)
comment at the bottom of the listing.

!!! kali "Read the flag from the SMB server string"
    ```bash
    smbclient -L //<target_ip> -N
    ```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Executable | `smbclient` | Literal | The SMB client program. |
| Option | `-L` | Literal | List the shares and server information. |
| Target | `//<target_ip>` | Replace the IP; keep `//` | Connect to the assigned target. |
| Option | `-N` | Literal | Connect without a password. |

Look for the `OCR{<flag_here>}` value in the server string shown alongside the
share listing. The same string also appears in the version-scan banner. You can
retrieve it with a targeted version scan:

```bash
nmap -sV -p 445 <target_ip>
```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Executable | `nmap` | Literal | The Nmap program. |
| Option | `-sV` | Literal | Enable service and version detection. |
| Option | `-p 445` | Literal | Scan only TCP port 445, the SMB port. |
| Target | `<target_ip>` | Replace | The IP from your exercise panel. |

Copy the whole flag value into the **Submit Flag** form on the platform and
click **Submit**. If the server string or banner is missing, do not guess a
flag; use the recovery table and ask your instructor.

### Completion evidence

Before you submit the flag, make sure you have:

- the exact `sudo whoami` result, or a note that the privilege check failed;
- the exact `sudo nmap -O` command and output;
- one row for each OS field, with observations separated from conclusions;
- a confidence value or an explicit “not shown”;
- an uncertainty statement explaining whether the result was one candidate,
  multiple candidates, or no exact match;
- the `smbclient` or `nmap -sV -p 445` command and output that produced the flag.

---

## What Just Happened?

You used Nmap's OS detection to collect network-behaviour evidence and compared
it with a fingerprint database. The result may be a single candidate, several
candidates, or no exact match. In every case, the useful output is the evidence
record: what Nmap printed, how strong the match was, and what you can honestly
conclude.

This exercise deliberately uses Linux with Samba emulating a Windows environment.
A Linux result or a Windows result can both be reasonable observations. The
lesson is to report the ambiguity instead of forcing certainty.

## Analysis Questions

**1. Why does OS detection require `sudo` when version detection (`-sV`) does
not?**

??? note "Reveal Answer"

    OS fingerprinting sends raw packets — hand-crafted packets that bypass the
    normal networking stack. Creating raw packets requires low-level access to
    the network interface, so the source command uses `sudo`. Version detection
    uses normal TCP connections that an unprivileged user can create. Because
    `sudo` grants elevated access, run only the intended command and do not leave
    a root shell open.

**2. The scan reports a 95% confidence value. What does that mean, and what does
it not mean?**

??? note "Reveal Answer"

    It means the target's response pattern matched that fingerprint closely. It
    does not mean there is a 95% probability that the operating system is exactly
    that version, and it does not rule out another candidate. Firewalls,
    virtualization, emulation, and custom network stacks can shift the
    fingerprint.

**3. Nmap reports no exact OS match. Did the exercise fail? What should you
record?**

??? note "Reveal Answer"

    No. OS detection is probabilistic, and an exact match is not guaranteed.
    Record that Nmap found no exact match. If it lists aggressive guesses, record
    them as guesses with their confidence values. State what the evidence does
    and does not support. A clear uncertainty statement is a valid result.

**4. The lab runs Linux with Samba emulating Windows, and Nmap reports a Windows
candidate. How should you report that?**

??? note "Reveal Answer"

    Report the observation (“Nmap printed a Windows Server 2019 candidate”) and
    the fingerprint evidence. Then state the limitation: the lab intentionally
    emulates Windows on Linux, so the result is a candidate, not a confirmed
    fact. Do not choose the Windows candidate merely because the scenario sounds
    Windows-like.

**5. How would knowing the likely OS change your next steps without
overclaiming?**

??? note "Reveal Answer"

    It helps you prioritise research, choose relevant administration or
    post-exploitation tools, and decide which privilege-escalation paths to
    investigate. It does not prove that a specific exploit will work. Confirm the
    version and configuration with other evidence before making a vulnerability
    claim.

## Defensive Takeaways

- Keep an inventory of operating-system versions and patch levels.
- Do not rely on hiding the OS or its banner as a security control; segmentation,
  access control, and patching matter more.
- Restrict management and file-sharing ports to authorized networks.
- Monitor for OS-detection scans and unusual probe patterns.
- Treat fingerprinting results as estimates and verify before acting on them.

## If You Get Stuck

| Symptom | Likely cause | What to do |
|---|---|---|
| `sudo` asks for a password you do not have, or permission is denied | The current account lacks the required privilege. | Use the provided RangeBox/Kali environment and ask your instructor. Do not try to bypass `sudo`. |
| The scan reports no OS details, or a very limited response | The target has filtered ports, limited responses, or a network path that prevents reliable fingerprinting. | Confirm the lab is **Running**, the target IP is correct, and the VPN/RangeBox is connected. Record the limitation instead of guessing. |
| Nmap reports several OS candidates | The fingerprint matches more than one known signature. | Record all candidates and their confidence values. State that the evidence is ambiguous. |
| Nmap reports no exact OS match | OS detection is probabilistic, or the responses were non-ideal. | Record “no exact match.” If aggressive guesses are listed, record them as guesses. This is not a failed lab. |
| `Host seems down` | Discovery probes were blocked, or the target is not ready. | Verify the target IP and VPN/RangeBox first. Do not assume the host is down. Do not add options by guessing. |
| `smbclient` or the version-scan banner does not show the flag | The share or service is not present, or the target is not the expected one. | Confirm the target IP and lab status. Ask your instructor if the lab does not match the scenario. |
| The flag is rejected | The value was copied incorrectly, or the wrong case/format was submitted. | Copy the whole `OCR{...}` value exactly. Do not guess or alter the flag. |

## Further Reading

- [Nmap OS detection](https://nmap.org/book/man-os-detection.html)
- [Nmap OS detection methods](https://nmap.org/book/osdetect-methods.html)
- [Nmap reference guide](https://nmap.org/book/man.html)
- [NIST National Vulnerability Database](https://nvd.nist.gov/)

## Key Takeaways

- OS fingerprinting is **inference from network behaviour**, not direct access to
  the target.
- `sudo nmap -O <target_ip>` is the source command. `sudo` is used because OS
  detection sends raw packets, and it grants elevated access that must be handled
  carefully.
- A result may be one candidate, several candidates, or no exact match. All three
  are valid outcomes.
- A confidence value is a fingerprint-match score, not a guarantee or a
  probability that the OS is exactly that version.
- Record observations, fingerprint evidence, confidence, and conclusions
  separately. Report uncertainty instead of inventing an exact OS.
- The lab deliberately emulates Windows on Linux, so a Linux or Windows result
  can both be reasonable observations.
- The next exercise combines port scanning, version detection, and OS detection
  into a single scan.
