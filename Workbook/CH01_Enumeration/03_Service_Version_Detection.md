# Exercise 1.3: Service Version Detection

## Before You Begin

In Exercise 1.1 and Exercise 1.2, the SERVICE column in your scan results was
based on the port number. Nmap looked up the port in its service list and printed
the service usually associated with it. That is a useful guess, but it is not a
confirmed product or version.

This exercise teaches you to probe the open ports for more detail and, just as
importantly, to separate what Nmap reported from what you can reasonably
conclude.

### Where the commands run

Run every command inside the **RangeBox** terminal (the browser-based lab
desktop) or your own **VPN** (Virtual Private Network)-connected Kali Linux VM.
Do not run them in the OpenCyberRange web page, on the platform server, or on the
target itself.

### What you need

- [ ] The Chapter 1 Introduction, Exercise 1.1, and Exercise 1.2 completed.
- [ ] The lab started and its status shown as **Running**.
- [ ] The target IP copied from the **Active Lab View** or **Exercise Network**
      panel.
- [ ] A terminal in the RangeBox or your VPN-connected Kali VM.
- [ ] A notes file for commands, output, observations, and conclusions.

### Estimated time

About **25–35 minutes**. Version detection takes longer than a basic scan because
Nmap probes each open port, and the interpretation step is part of the work.

### Scope

!!! warning "Authorized target only"
    Scan only the target IP shown in this exercise. Do not scan the platform,
    your RangeBox, other students, your school or employer network, or the
    internet. If the panel does not show a target, stop and ask your instructor;
    do not scan addresses at random.

### What you will be able to do

By the end of this exercise, you will be able to:

- distinguish a port number, service name, product, version, and banner;
- explain how version detection works and why its result is an estimate;
- run `nmap -sV` against the assigned target;
- read the PORT, STATE, SERVICE, and VERSION columns;
- record an observation separately from a conclusion;
- use a version string as a research and prioritisation lead without claiming
  that it proves exploitability;
- retrieve and submit the flag.

## Scenario

You are continuing the FinanceCorp network assessment. James Mitchell, the IT
director, has reviewed your port scan results and wants more detail. Knowing
that ports 80, 445, and 3389 are open is a start, but the security team needs
software names and version evidence before they can decide what to research.
Your job is to run a version detection scan and deliver precise findings.

## Your Objectives

- Use Nmap version detection (`-sV`) to collect service and version evidence.
- Distinguish service names, products, and versions in the output.
- Record observations separately from conclusions.
- Explain which findings are strong evidence and which are uncertain.
- Retrieve and submit the flag.

## Background: From Port Number to Evidence

Version detection adds detail, but the detail has different layers. Keep these
terms separate.

| Term | Meaning | Example from this exercise |
|---|---|---|
| **Port number** | The numbered endpoint Nmap connected to. | `445/tcp` |
| **Service name** | Nmap's label for the protocol or service. It is often based on the port or a protocol signature and can change when version detection runs. | `netbios-ssn` |
| **Product** | The software family or application name. | `Samba` (with the daemon name `smbd`) |
| **Version** | The specific release string reported by the service or inferred from its response. It may be missing, partial, or inaccurate. | `4.15.5` |
| **Banner** | The text or protocol response a service returns when probed. Nmap uses banners and other responses to infer the product and version. A banner may be missing, masked, or deliberately misleading. | A Samba or SSH identification string |
| **Signature** | A pattern Nmap matches against a service response to identify a product or protocol. | An HTTP response pattern associated with nginx |
| **CVE** | Common Vulnerabilities and Exposures: a standardized identifier for a publicly known vulnerability. | `CVE-2024-12345` |
| **Security advisory** | A notice from a vendor or authority about a vulnerability, affected versions, and remediation. | A vendor bulletin listing a fixed release |
| **Exploitability** | Whether a weakness can actually be exploited in a specific configuration. A version match alone does not establish it. | A version match is a research lead, not proof |

### What version detection actually does

When you pass `-sV`, Nmap sends protocol-specific probes to each open port: HTTP
requests, SMB negotiation packets, TLS handshakes, and many other protocol
signatures. It compares the responses with its `nmap-service-probes` database
and reports the best match in the VERSION column.

The result is **evidence**, not a guarantee. Nmap is inferring from what the
service exposes. A custom application can return a standard-looking banner. A
proxy or port forward can hide the real service. A service can suppress its
version string. A vendor can backport security fixes without changing the
version number. Treat every version string as an estimate that needs
corroboration.

### Worked output-reading example

!!! note "Representative output, not your output"
    The example below is from the reference setup. Your target, Nmap version,
    service names, and version strings may differ. Record what your scan
    actually prints. A version string is not proof of exploitability.

```text
Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for 10.100.13.10
Host is up (0.0031s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE        VERSION
80/tcp   open  http           nginx 1.24.0
445/tcp  open  netbios-ssn    Samba smbd 4.15.5
3389/tcp open  ms-wbt-server  xrdp

Nmap done: 1 IP address (1 host up) scanned in 12.84 seconds
```

Read the table one column at a time:

| Port | State | Service name | Product | Version | What the line is evidence of |
|---|---|---|---|---|---|
| `80/tcp` | `open` | `http` | `nginx` | `1.24.0` | Nmap matched an HTTP response to an nginx signature and extracted a version string. |
| `445/tcp` | `open` | `netbios-ssn` | `Samba` (`smbd`) | `4.15.5` | Nmap matched an SMB response to Samba and extracted a version string. The service label also changed from the basic scan's `microsoft-ds`. |
| `3389/tcp` | `open` | `ms-wbt-server` | `xrdp` | not shown | Nmap identified an RDP product but did not report a version. The product is known; the version is unknown. |

Notice the difference between the service name and the product:

- `http` and `netbios-ssn` are Nmap service labels. They describe the protocol
  or conventional service, not the software vendor.
- `nginx` and `Samba` are products.
- `1.24.0` and `4.15.5` are versions.
- For `3389/tcp`, `xrdp` is a product, but no version is shown. You cannot make a
  version-specific research claim from that line alone.

### Observations and conclusions are different

Record what the tool printed before you interpret it.

| Record type | Example |
|---|---|
| **Observation** | “Nmap reported `Samba smbd 4.15.5` for `445/tcp` with state `open`.” |
| **Supported conclusion** | “The SMB service is probably Samba 4.15.5. This is a research lead for the next phase.” |
| **Not supported** | “The host is vulnerable to a specific Samba CVE.” A version match alone does not establish that. |

A version string supports **research and prioritisation**: which advisories to
read, which patch level to compare, and which service deserves attention first.
It does not prove that the service is vulnerable or exploitable in this
configuration.

!!! warning "A version is not a vulnerability finding"
    A version match can be useful, but it is not proof. The version may be
    patched or backported, the banner may be masked or wrong, the service may be
    behind a proxy, and the configuration may not be exploitable. Claim a
    vulnerability only after checking an authoritative advisory and, where the
    workbook provides it, verifying the behaviour.

## Tool Primer: `nmap -sV`

!!! kali "Add the version detection option"
    The version detection scan adds one option to the basic command:

    ```bash
    nmap -sV <target_ip>
    ```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Executable | `nmap` | Literal | The Nmap program. |
| Option | `-sV` | Literal | Enable service and version detection. Nmap probes each open port instead of only guessing from the port number. |
| Target | `<target_ip>` | Replace | The IP from the Active Lab View or Exercise Network panel for your session. |

The exercise uses `-sV`. Nmap also has `--version-intensity <0-9>` to control how
many probes it sends; the default is 7. Higher values try more probes and take
longer, while lower values are faster but may miss a service. You do not need to
change the intensity for this exercise.

**What success looks like**

- The scan completes and prints a VERSION column.
- At least one line gives a product or version string you can record.
- You can separate the service label, product, and version for each line.
- You can state which lines have no version and therefore cannot support a
  version-specific conclusion.

**Normal uncertainty**

- The VERSION column may be empty, say `unknown`, show only a product, or contain
  a generic string.
- Nmap may show `tcpwrapped` when a service accepts a connection but does not
  reveal enough to identify itself.
- The service name may change between the basic scan and the version scan. That
  is expected; it is a label, not a guarantee.
- The reported version may be incomplete or wrong. Record it as an observation
  first.

**Likely failure paths**

- Running the command on the wrong target, or using an example IP instead of the
  active target.
- Running before the lab is ready or before the VPN is connected, which produces
  timeouts or unreachable-host results.
- Forgetting that `-sV` is the option and `<target_ip>` is the value you replace.
- Assuming a version string proves a vulnerability. It does not.
- Treating a missing version as “no service” or “secure.” It means the evidence
  is incomplete.

## Walkthrough

### Step 1: Launch the exercise

1. Navigate to **Exercises** and locate the **Service Version Detection** lab.
2. Click **Launch** and wait for the status to change to **Running**.
3. Copy the **target IP** from the **Active Lab View** or **Exercise Network**
   panel into your notes.

Every command uses the placeholder `<target_ip>`. Replace it with the target IP
from your exercise panel. Do not copy an example IP from the introduction or
another student's screen.

### Step 2: Run a basic scan as a baseline

!!! kali "Run a basic scan as a baseline"
    In the RangeBox terminal or your VPN-connected Kali VM, run:

    ```bash
    nmap <target_ip>
    ```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Executable | `nmap` | Literal | The Nmap program. |
| Options | none | — | The default TCP scan of the 1,000 most common ports. |
| Target | `<target_ip>` | Replace | The IP from your exercise panel. |

Record the open ports and the SERVICE column. In the reference setup you may see
labels such as `http`, `microsoft-ds`, and `ms-wbt-server`. These are port-based
guesses. Your output may differ; record what it actually says.

### Step 3: Run version detection

!!! kali "Run version detection"
    Now run the same scan with `-sV`:

    ```bash
    nmap -sV <target_ip>
    ```

    The `-sV` scan takes longer because Nmap is probing each open port with
    protocol-specific requests. Watch the progress indicator and let it finish.

When the scan completes, copy the full output into your notes. Pay attention to
the VERSION column. It may contain a product name, a version, both, or neither.

### Step 4: Read the output as evidence

Use the worked example above as a model. For each open port, record:

| Field | What to write |
|---|---|
| Port and state | For example, `445/tcp open` |
| Service name | The SERVICE label Nmap printed |
| Product | The software name, if present |
| Version | The version string, if present, or “not shown” |
| Banner/evidence | What Nmap used, if the output or the service response makes it visible |
| Observation | A factual sentence about what Nmap printed |
| Tentative conclusion | What the observation supports, with an uncertainty note |

For the reference example:

- `80/tcp` reports product `nginx` and version `1.24.0`. The observation is that
  Nmap matched an HTTP response to nginx 1.24.0. A tentative conclusion is that
  the web service is probably nginx 1.24.0; this is a research lead, not proof of
  a vulnerability.
- `445/tcp` reports service `netbios-ssn`, product `Samba` (`smbd`), and version
  `4.15.5`. The basic scan's `microsoft-ds` label was a port-based guess; the
  version scan gives a more specific product and version. It still does not prove
  exploitability.
- `3389/tcp` reports product `xrdp` but no version. Record the product and write
  “version not shown.” You cannot make a version-specific claim from this line.

Use this table to record your own output. Keep the observation factual; put your
interpretation in the conclusion column.

> **My version scan record**
>
> | Port | State | Service name | Product | Version | Observation (what Nmap printed) | Tentative conclusion |
> |---|---|---|---|---|---|---|
> |  |  |  |  |  |  |  |
> |  |  |  |  |  |  |  |
> |  |  |  |  |  |  |  |
>
> **Evidence quality check:**
>
> - Which rows have a product but no version?
> - Which rows have a version you would need to corroborate before relying on it?
> - Which conclusions are supported by more than one observation?

### Step 5: Retrieve the flag

The version scan reports Samba on port 445. The target exposes an anonymous
share named `public` that holds a `flag.txt` file. Use `smbclient` to connect
without a password and print the file to your terminal:

!!! kali "Read the flag from the SMB public share"
    ```bash
    smbclient //<target_ip>/public -N -c 'get flag.txt -'
    ```

| Part | Example | Literal or replaceable | Meaning |
|---|---|---|---|
| Executable | `smbclient` | Literal | The SMB client program. |
| Target and share | `//<target_ip>/public` | Replace the IP; keep `/public` | Connect to the `public` share on the assigned target. |
| Option | `-N` | Literal | Connect without a password. |
| Option | `-c` | Literal | Run the command that follows. |
| Command | `'get flag.txt -'` | Literal | Download `flag.txt`. The trailing `-` prints it to standard output instead of saving it to disk. |

Chapter 2 covers `smbclient` in depth. The output contains the flag in
`OCR{<flag_here>}` format. Copy the whole value, paste it into the **Submit
Flag** form, and click **Submit**.

If the share or file is not present, do not guess a flag. Use the recovery table
below and ask your instructor if the lab does not match the scenario.

### Completion evidence

Before you submit the flag, make sure you have:

- the exact basic scan command and its open ports;
- the exact `-sV` command and its full output;
- a row for each open port that separates service name, product, version, and
  observation;
- at least one tentative conclusion clearly labelled as a conclusion;
- at least one uncertainty, such as a missing version or a generic banner;
- the `smbclient` command and output that produced the flag.

---

## What Just Happened?

You ran a basic scan, then a version detection scan, and compared the two. The
basic scan gave you port-based service guesses. The version scan gave you product
and version evidence where the services exposed enough information.

The useful result is not just the VERSION column. It is the evidence record:
what Nmap printed, which parts are product versus version, which lines are
missing a version, and which conclusions are supported by the evidence. A version
string is a research lead. It is not a vulnerability finding.

## Analysis Questions

**1. Why is “Samba smbd 4.15.5” more useful than “microsoft-ds” for research, and
what does it still not prove?**

??? note "Reveal Answer"

    The version string names a product and a version, so you can search
    authoritative advisories for Samba 4.15.5, compare it with the current
    patched release, and decide whether it deserves attention. It does not prove
    that the service is vulnerable or exploitable: the version may be patched or
    backported, the banner may be wrong, and the configuration may not be
    exploitable.

**2. You found nginx on port 80 instead of Microsoft IIS. What does that suggest
about the server, and how certain should you be?**

??? note "Reveal Answer"

    Nginx is commonly deployed on Linux and Unix systems, so it suggests the
    host may be Linux rather than Windows. Treat that as an inference, not a
    fact. Confirm it with operating-system evidence before relying on it. The
    platform matters because administration, privilege escalation, and
    post-exploitation steps differ between operating systems.

**3. How would you use the version string “Samba smbd 4.15.5” in the next phase
without overclaiming?**

??? note "Reveal Answer"

    Search authoritative vulnerability and vendor advisory sources for Samba
    4.15.5, check whether the version is still supported, compare it with the
    patched release, and check whether the configuration exposes the service. A
    match is a prioritisation lead. Claim a vulnerability only after reading an
    authoritative advisory and, where the workbook provides it, verifying the
    behaviour. Remember that a vendor may backport a fix (apply it to an older
    version without changing the version number), so the version string alone
    may not reflect the patch level.

**4. Nmap reports `xrdp` on port 3389 but no version. What can you conclude, and
what can you not conclude?**

??? note "Reveal Answer"

    You can record that Nmap identified the RDP product as xrdp. You cannot make
    a version-specific vulnerability claim because no version was reported. That
    is a normal uncertainty; record it as “product identified, version not
    shown” and continue with other evidence.

**5. What would make you doubt a version string even when Nmap prints one?**

??? note "Reveal Answer"

    A custom banner, a proxy or port forward, a deliberately masked version, a
    `tcpwrapped` result, or a service that behaves differently from its banner.
    Also consider backported fixes: a vendor can keep an old version number while
    including security patches. Corroborate before relying on the version.

## Defensive Takeaways

- Keep an inventory of software versions and patch levels; you cannot manage what
  you do not know.
- Patch or mitigate exposed services based on vendor advisories and configuration,
  not on a banner match alone.
- Do not rely on hiding a version banner as a security control. Restrict access,
  authenticate, and patch.
- Monitor for version-detection scans and unusual service probing.
- Treat scanner output as evidence to verify, not a final vulnerability report.

## If You Get Stuck

| Symptom | Likely cause | What to do |
|---|---|---|
| The scan times out or all ports are filtered | VPN not connected, target not ready, or a firewall is blocking the path. | Check the platform's VPN status, confirm the lab is **Running**, and try again. If using RangeBox, confirm the desktop is connected. |
| `Host seems down` | Nmap's discovery probes were blocked, or the target is not ready. | Verify the target IP and VPN/RangeBox first. Do not assume the host is down. Do not add options by guessing; follow the course guidance. |
| VERSION is empty or says `unknown` | The service did not expose enough information, or the signature did not match. | Record the uncertainty. Do not invent a product or version. Use the other evidence available. |
| The scan reports `tcpwrapped` | The service accepted a connection but did not reveal enough to identify itself. | Record it as incomplete evidence. Do not treat it as “secure” or “no service.” |
| The service label changed from the basic scan | The version probe identified a different protocol label. | Record both labels and explain the difference. The service name is a label, not a guarantee. |
| `smbclient` fails to read `flag.txt` | The share or file is not present, or the target is not the expected one. | Confirm the target IP and exact share/file names. Ask your instructor if the lab does not match the scenario. |
| The flag is rejected | The value was copied incorrectly, or the wrong case/format was submitted. | Copy the whole `OCR{...}` value exactly. Do not guess or alter the flag. |

## Further Reading

- [Nmap version detection](https://nmap.org/book/man-version-detection.html)
- [Nmap port scanning basics](https://nmap.org/book/man-port-scanning-basics.html)
- [NIST National Vulnerability Database](https://nvd.nist.gov/)
- [CVE Program](https://www.cve.org/)

## Key Takeaways

- A port number, service name, product, and version are different pieces of
  evidence. Keep them separate.
- `-sV` makes Nmap probe open ports for product and version evidence instead of
  guessing only from the port number.
- Version detection is an estimate. Banners and signatures can be missing,
  masked, or wrong.
- A version string supports research and prioritisation. It does not prove that a
  service is vulnerable or exploitable.
- A missing version is a valid observation. Record the uncertainty instead of
  filling it in.
- The next exercise uses operating-system detection, another estimate that needs
  careful interpretation.
