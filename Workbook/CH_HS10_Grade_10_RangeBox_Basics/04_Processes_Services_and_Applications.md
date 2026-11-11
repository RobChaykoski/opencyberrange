# Processes, Services, and Applications

This activity connects familiar applications to running processes and network
services. You will use **read-only** commands. You will not stop a service, kill
a process, or change configuration.

This page does **not** ask you to contact a target. It uses RangeBox itself and
one example service from the applied labs.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Assigned target** | A practice server named in a lab. | **Not contacted in this activity.** The example service is `network.lab:8080` from the Network Basics lab. |

### What you need

- [ ] The RangeBox terminal open.
- [ ] The skills from [Command Line Fluency](02_Command_Line_Fluency.md).
- [ ] A notes file for the relationship table.
- [ ] About **20–30 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain program, process, process ID, parent process, application, service,
  daemon, port, listener, and client connection;
- identify one process and its parent without changing anything;
- identify one listening service, or explain why none is visible;
- connect an application, process, service, port, and purpose in a table;
- explain why a process is not the same as a service.

## Words to Know

| Term | What it means |
|---|---|
| **Program** | A file on disk that contains instructions. |
| **Process** | A running instance of a program. |
| **Process ID (PID)** | The number the operating system uses to identify a process. |
| **Parent process** | The process that started another process. |
| **Application** | A program a user opens, such as a browser or terminal. |
| **Service** | A program that provides something to other programs or users, often over a network. |
| **Daemon** | A background service process that usually has no terminal window. |
| **Port** | A number that identifies which service on a host should receive a connection. |
| **Listener** | A socket waiting for incoming connections, usually shown as `LISTEN`. |
| **Client connection** | A connection from a client process to a service. It usually has a local and remote address. |

## Process, Service, Application

These words describe different layers:

| Layer | Example | What it means |
|---|---|---|
| **Application** | A terminal window or browser | What the user opens. |
| **Process** | A running shell or browser process | The program while it is running. |
| **Service** | A web service on port 8080 | A program that provides something. |
| **Port** | `8080` | The number a client uses to reach the service. |
| **Listener** | `LISTEN` on port 8080 | The service is waiting for connections. |
| **Client connection** | Browser to `network.lab:8080` | A client has connected to the service. |

An application can start several processes. A process is not automatically a
service. A service is a process, or a set of processes, that provides something.
A port is a number, not a physical opening.

## Walkthrough

### Step 1: Find your shell process

```bash
ps -o pid,ppid,comm -p $$
```

**Why:** `$$` is the process ID of the current shell. `-o` chooses the columns:
process ID, parent process ID, and command name. `-p` selects that process.

**Expected result:** a short table with a PID, a PPID, and a command name such as
`bash` or `zsh`. Your numbers will be different.

**What to notice:** the shell is a **process**. The terminal window is the
**application** that contains it.

### Step 2: Find the parent process

```bash
ps -o pid,ppid,comm -p $PPID
```

**Why:** `$PPID` is the parent process ID. This shows what started your shell.

**Expected result:** one process, often a terminal or session process. The name
may be different on your desktop.

**If the command shows an error:** the shell may not set `$PPID` the same way.
Write down the PPID from Step 1 and use it as a replaceable value:

```bash
ps -o pid,ppid,comm -p PPID
```

Replace `PPID` with the number from Step 1.

### Step 3: List listening sockets

```bash
ss -tuln
```

**Why:** `ss` shows network sockets. The options mean:

- `-t`: TCP;
- `-u`: UDP;
- `-l`: listening sockets only;
- `-n`: show numbers instead of names.

**Expected result:** zero or more lines. A TCP listener usually shows `LISTEN` in
the State column, a local address, and a port.

**If no lines appear:** no listening service is visible in this RangeBox
container. That is a valid result. Write "no listener visible" and use the
example service in the relationship table.

**If the command is not found:** use `netstat -tuln` if your desktop provides it.
If neither works, ask your teacher. Do not install a tool.

### Step 4: Read one listener

Choose one line with `LISTEN`, if one is shown. Write down:

- the local address;
- the port;
- the process name, if shown.

To include the process name, you can try:

```bash
ss -tulnp
```

**Why:** `-p` asks for the process using the socket. It may show a name only for
processes you own.

**Expected result:** the same listeners with a process name where available. If
the process name is blank or `-`, that is normal for processes you do not own.

**Do not** use `sudo` to see more. Stop with what you have.

### Step 5: List established TCP connections

```bash
ss -tn
```

**Why:** this shows TCP sockets, including established client connections.
`-t` means TCP and `-n` means numeric addresses.

**Expected result:** zero or more lines. If you have a browser tab open to a
service, you may see an established connection with a local and remote address.

**If no connections appear:** that is normal when nothing is connected. Open no
new sites just to create one.

### Step 6: Build the relationship table

Copy this table into your notes and fill in one row for your shell and one row
for a service.

| Application | Process | Service | Port | Purpose | Evidence |
|---|---|---|---|---|---|
| RangeBox terminal | shell process | none | none | Type commands | `ps -o pid,ppid,comm -p $$` |
| RangeBox browser | browser process | client connection | local port + remote port | View a page | `ss -tn` |
| Network Basics target | server process (on the target) | HTTP | 8080 | Return a status page | `network.lab:8080` from the lab page |

**Why:** the table makes the relationship visible. It also shows what you did
**not** observe.

**Expected result:** at least two completed rows, with "not visible" or
"example only" where appropriate.

## What Not to Do

Do **not** run any of these in this activity:

- `kill` or `pkill`;
- `systemctl stop`, `service stop`, or `shutdown`;
- `sudo`;
- configuration changes;
- port scans.

This activity is observation only. A process or service that is running is not
automatically a security problem.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| `ps` shows no process | The PID or shell variable is wrong | Run `echo $$` and use that number with `ps -p`. |
| `$PPID` is empty | The shell does not provide it | Use the PPID from the `ps` output. |
| `ss` is not found | `command not found` | Try `netstat -tuln`. If that fails, ask. Do not install tools. |
| No listeners | An empty result | Record "no listener visible" and use the example service. |
| No connections | An empty result | This is normal. Do not browse to create one. |
| Process name is blank | `-` or empty | You do not have permission to see it. Do not use `sudo`. |
| You are unsure what a line means | A long address or port | Write it down and ask. Do not stop the process. |

## Record Your Evidence

| Question | Your answer |
|---|---|
| What was your shell PID? | |
| What was its parent PID? | |
| What command name did the shell show? | |
| Did `ss -tuln` show a listener? | |
| If yes, what local address and port? | |
| Did `ss -tn` show an established connection? | |
| Which row of the relationship table is observation, and which is an example? | |

Then answer:

1. What is the difference between a program and a process?
2. What is a PID?
3. What is a parent process?
4. What is a service?
5. What is a daemon?
6. What is a listener?
7. What is a client connection?
8. Why is a running service not automatically a vulnerability?

## What Success Looks Like

You are ready to continue when you can show:

- one shell process and its parent;
- one listener, or a clear note that none was visible;
- one client connection, or a clear note that none was visible;
- a relationship table with application, process, service, port, purpose, and
  evidence;
- a clear statement that you did not stop, kill, or change anything.

This activity has **no flag**. Your evidence is your table and your explanation.

## Key Takeaways

- A program is a file; a process is a running instance.
- A PID identifies a process; a parent process started it.
- An application can start processes. A service is a process that provides
  something.
- A listener waits for connections; a client connection reaches a service.
- A port is a number, not a physical opening.
- Observation is not authorization to stop, kill, or change a service.
- Do not use `sudo` to see more.

Next: [Network Communication and Ports](05_Network_Communication_and_Ports.md).
