# Exercise L1.1: Workspace and Module Discipline

## Before You Begin

- Confirm the lab is running and that you can reach the target from your Kali
  RangeBox.
- KVM acceleration is used when available. Without `/dev/kvm` the target uses
  software emulation, so the first boot can take several minutes.
- Work only inside the isolated lab network. Do not scan or attack any system
  outside the exercise.
- Keep a notebook open. Record the command, the output, and the reason for each
  action.

## Scenario

Northwind Freight has asked your team to begin a small, authorised assessment of
one of its training systems. The project lead wants clean evidence from the
first command: a named workspace, a working database connection, and a module
chosen from its metadata rather than from a memorised name.

Your Kali RangeBox already has the Metasploit Framework installed. The target is
a deliberately vulnerable training host on the isolated lab network. Nothing in
this exercise requires exploiting a service; the goal is disciplined setup and
module selection.

## Your Objectives

- Configure a Metasploit workspace and confirm database connectivity.
- Identify a module's purpose, platform, and required options from its metadata.
- Document the selected module and target service in the workspace.
- Retrieve the target web flag and record the command that produced it.

## Background

A Metasploit workspace separates the hosts, services, credentials, and notes for
one engagement from every other engagement stored in the same database. Without
a workspace, scan results blur together and evidence becomes difficult to
reproduce.

Modules also carry metadata: a name, a description, a platform, a rank, and a
set of options. Reading that metadata first is the difference between selecting a
module because it fits the target and guessing from a search result.

## Workspaces and evidence

A workspace is a named container for hosts, services, credentials, loot, and
notes. Use one workspace per engagement. Before you scan, confirm the database
is connected with `db_status`; a console without a database still runs modules,
but it cannot build the evidence trail you will need later.

The workspace name is part of your evidence. Record it in your report and keep
it stable for the whole engagement.

## Reading module metadata

`search` finds modules. `info` tells you what a module does, which platforms it
supports, its reliability rank, and which options it expects. `show options`
lists the current values after you select the module.

A disciplined operator checks the module rank, the target platform, and the
required options before running anything. If a module needs a payload, confirm
that the payload matches the target architecture.

## Guided Steps

1. **Start the console.** Run `msfconsole -q` and wait for the `msf6 >` prompt.
2. **Check the database.** Run `db_status`. The output should report a connection to the PostgreSQL database.
3. **Create a workspace.** Run `workspace -a northwind` and then `workspace`. Confirm `northwind` is the current workspace.
4. **Search by capability.** Run `search type:auxiliary name:ssh_version`. Read the returned module names and ranks.
5. **Read module metadata.** Run `use auxiliary/scanner/ssh/ssh_version` and then `info`. Note the description, platform, and options.
6. **Inspect options only.** Run `show options`. Identify `RHOSTS`, `RPORT`, and `THREADS`. Do not run the module yet.
7. **Set the target.** Run `set RHOSTS target`, `set RPORT 22`, and `show options` again to confirm the values.
8. **Run the scanner.** Run `run`. The scanner should identify the SSH service on the target.
9. **Review the database.** Run `services`. The target and port 22 should now be recorded in the current workspace.
10. **Collect the evidence flag.** From a Kali terminal, run `curl http://target/flag.txt` and record the flag.

## Flag

Submit the flag exactly as it appears in the lab. In your notes, record the
command and the location that produced it. A flag without a reproducible command
is not useful evidence.

## Defensive Takeaways

Inventory exposed management services, restrict them to administration networks, and log scanner-style connection attempts. A clean workspace is also a defensive habit: it makes later evidence review possible.

## Further learning and credits

This exercise is original OpenCyberRange practice. It is **not affiliated with,
endorsed by, or derived from OffSec course materials**.

For a free structured course on the Metasploit Framework, see
[Metasploit Unleashed](https://www.offsec.com/metasploit-unleashed/) by OffSec.
If you use that course, please support **Hackers For Charity**, a 501(c)(3)
nonprofit. A **$9 donation feeds a child for a month**.

- [Donate via OffSec](https://www.offsec.com/metasploit-unleashed/donate/)
- [Hackers For Charity](https://www.hackersforcharity.org/donate/)
