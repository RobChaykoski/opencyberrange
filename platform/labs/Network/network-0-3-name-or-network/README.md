# Name or Network? Troubleshooting a Broken Portal

## Lab Overview

This capstone lab for Network Foundations combines ping and DNS. The ticket says
a portal is down, but the ticket uses an old name. You must decide whether the
problem is the **name**, the **host**, or the **service** before you change
anything.

**Difficulty:** Beginner  
**Estimated Time:** 25–30 minutes  
**Focus:** Network troubleshooting / DNS

## Prerequisites

- Completed **Can You Reach It? Ping Fundamentals**
- Completed **The Internet's Phone Book: DNS Records**

## Learning Objectives

By completing this lab, you will:

1. Separate a name-resolution problem from a reachability problem.
2. Use DNS TXT records to find operational notes.
3. Confirm a corrected name with ping.
4. Read the service page and capture the flag.

## Background

A user says "the portal is down." That sentence could mean at least three
different things:

| Layer | Question | Tool |
|---|---|---|
| **Name** | Does the name resolve to the right address? | `dig`, `nslookup` |
| **Host** | Is the address reachable? | `ping` |
| **Service** | Is the application running on the expected port? | `curl`, browser |

Good troubleshooting works down those layers instead of guessing. A stale DNS
record can make a healthy service look dead. A dead service can make a healthy
host look broken.

## Step-by-Step Walkthrough

### Step 1: Check the name in the ticket

```bash
dig @<target> stale.range.local A +short
```

The result is `192.0.2.99`. That address belongs to TEST-NET-1, a documentation
range that is not routed on this lab network. The name is stale.

### Step 2: Read the operational note

```bash
dig @<target> _note.range.local TXT +short
```

The TXT record says the portal moved and points at `portal.range.local`.

### Step 3: Resolve the current name

```bash
dig @<target> portal.range.local A +short
```

The answer is the lab host's current IP address.

### Step 4: Confirm the host

```bash
ping -c 4 <current-ip>
```

A reply proves the host is reachable. If ping failed here, you would have a host
or path problem rather than a name problem.

### Step 5: Check the service

```bash
curl http://<current-ip>/
```

The page contains the flag. It also summarizes what each check proved.

### Step 6: Submit the flag

```bash
curl -s http://<current-ip>/ | grep -o 'OCR{[^}]*}'
```

## Analysis Questions

1. Why did `ping stale.range.local` fail?
2. What did the TXT record tell you that the A record did not?
3. If the new name resolved but ping failed, what would you check next?
4. If ping succeeded but `curl` failed, what would that tell you?
5. Why is it risky to "fix" a problem before identifying which layer is broken?

## Common Mistakes

### Mistake 1: Replacing the DNS record before reading the note

The TXT record is the operational clue. Read it first.

### Mistake 2: Assuming a failed ping means the host is off

The stale name points at a documentation address, so the failure is expected.
The failure is in the name, not necessarily the network.

### Mistake 3: Stopping after ping succeeds

Ping proves the host. It does not prove the service is running. Always check the
service you actually need.

## Key Takeaways

- Troubleshoot down the layers: name, host, service.
- A stale DNS record can make a healthy service unreachable.
- TXT records are often used for operational notes and policy.
- Each tool answers a different question; none of them answers all of them.

## Next Step

Continue to **CH N1 -- Log Analysis** to see how these network events look in
firewall and DNS logs.
