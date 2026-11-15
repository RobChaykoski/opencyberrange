# Exercise L1.2: Auxiliary Service Discovery

## Before You Begin

- Confirm the lab is running and that you can reach the target from your Kali
  RangeBox.
- This lab requires a KVM-capable host. If the platform reports that the lab
  cannot start, ask the instructor to check `/dev/kvm`.
- Work only inside the isolated lab network. Do not scan or attack any system
  outside the exercise.
- Keep a notebook open. Record the command, the output, and the reason for each
  action.

## Scenario

The Northwind training host exposes several legacy services. Your task is to
build a service inventory with Metasploit auxiliary scanners, not with a single
blind port scan. The inventory should identify the protocol and the version for
each reachable service so the next exercise can choose a validation target.

Stay inside the lab network. The target is intentionally vulnerable and must
never be exposed to an untrusted network.

## Your Objectives

- Run a TCP port scan with an auxiliary module.
- Identify SSH, FTP, HTTP, and MySQL versions with service-specific scanners.
- Store and review results in the workspace database.
- Explain why version evidence matters before exploitation.
- Retrieve the target flag from the web service.

## Background

Auxiliary modules do not open a session. They gather information, validate a
configuration, or interact with a service. Service-specific scanners are often
more useful than a generic port scan because they understand the protocol
banner and report the software version.

Metasploit records scanner results as hosts and services. That record is the
bridge between reconnaissance and exploitation: a module can be selected from
the observed version instead of from a guess.

## Why service-specific scanners

A TCP port scan tells you that a port accepts connections. A protocol scanner
tells you what is behind the port and often which version is running. That
distinction matters when you choose an exploitation module: a service name is a
hint, but a version is evidence.

## Recording results

Metasploit writes hosts and services into the current workspace. After each
scanner, run `services` and confirm the result is present. If you change
workspaces, results from the previous workspace are no longer in scope.
Recording results as you go makes the final report reproducible.

## Guided Steps

1. **Confirm the workspace.** Run `workspace` and confirm you are in `northwind`.
2. **Scan common TCP ports.** Run `use auxiliary/scanner/portscan/tcp`, set `RHOSTS target`, set `PORTS 21,22,80,3306,8180`, and run it.
3. **Identify SSH.** Use `auxiliary/scanner/ssh/ssh_version` against the target and note the version.
4. **Identify FTP.** Use `auxiliary/scanner/ftp/ftp_version` and note the FTP banner.
5. **Identify HTTP.** Use `auxiliary/scanner/http/http_version` and note the web server version.
6. **Identify MySQL.** Use `auxiliary/scanner/mysql/mysql_version` and note the database banner.
7. **Review the inventory.** Run `services` and then `services -R` to display the recorded services and versions.
8. **Capture the flag.** Run `curl http://target/flag.txt` from a Kali terminal and record the flag.

## Flag

Submit the flag exactly as it appears in the lab. In your notes, record the
command and the location that produced it. A flag without a reproducible command
is not useful evidence.

## Defensive Takeaways

Reduce the exposed service set, remove legacy protocols from user networks, and alert on version-scanning patterns. Version data is reconnaissance: treat banners as information leakage.

## Further learning and credits

This exercise is original OpenCyberRange practice. It is **not affiliated with,
endorsed by, or derived from OffSec course materials**.

For a free structured course on the Metasploit Framework, see
[Metasploit Unleashed](https://www.offsec.com/metasploit-unleashed/) by OffSec.
If you use that course, please support **Hackers For Charity**, a 501(c)(3)
nonprofit. A **$9 donation feeds a child for a month**.

- [Donate via OffSec](https://www.offsec.com/metasploit-unleashed/donate/)
- [Hackers For Charity](https://www.hackersforcharity.org/donate/)
