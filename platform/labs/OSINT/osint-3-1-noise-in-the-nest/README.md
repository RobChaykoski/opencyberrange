# Lab 3.1: Noise in the Nest

## Learning Objectives

- Identify a canary token in a public document without triggering it by accident
- Distinguish a human browser visit from link-preview, scanner, and uptime-monitor traffic
- Explain what a canary alert proves and what it cannot prove
- Record an observation, inference, and unknown for a non-specialist

## Scenario

Northwind Freight published an incident update after a warehouse outage. The
press page links to an incident timeline. The link is a canary token managed by
the security team.

The console has three synthetic noise events: a link-preview bot, a
vulnerability scanner, and an uptime monitor. A browser-class visit unlocks the
lab flag and gives you a real event to triage.

## Solution Walkthrough

### Step 1: Inspect the public page

```bash
curl -s http://portal.lab/
```

The timeline link points at `http://canary.lab/t/incident-timeline`. In a real
investigation, you would inspect the source before clicking; here the token is
lab-owned and safe to trigger.

### Step 2: Trigger the token from a browser context

Open the link from the portal in the lab browser. If you are using a terminal,
send the navigation headers a browser would send:

```bash
curl -s -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Dest: document' \
  -H 'Referer: http://portal.lab/' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36' \
  http://canary.lab/t/incident-timeline
```

### Step 3: Read the console

```bash
curl -s http://canary.lab/console/api/events | python3 -m json.tool
```

Compare the events:

| Signal | Human navigation | Link preview | Scanner | Uptime monitor |
|---|---|---|---|---|
| `User-Agent` | browser string | bot string | scanner string | monitor string |
| `Referer` | `http://portal.lab/` | chat or social app | usually empty | empty |
| `Sec-Fetch-Mode` | `navigate` | usually empty | usually empty | usually empty |
| Timing | one-off | shortly after publication | repeated probes | regular interval |

The flag appears in the console after a browser-class hit. Record it from your
own lab instance and submit it on the platform; the value is not published here.

## What Just Happened?

A canary token is a tripwire. It tells you that a URL was requested. It does not
tell you who requested it, why, or whether the person who clicked is the person
who leaked the document.

The console shows three common sources of false positives:

- **Link previews** fetch links to build a card in a chat or social app.
- **Scanners** probe public URLs for known paths and vulnerabilities.
- **Uptime monitors** fetch the same URL on a schedule.

A browser-class hit is stronger evidence of a human visit, but still not proof
of identity or intent. The correct next step is to preserve the event, compare it
with other sources, and write a confidence-rated finding.

## Analysis Questions

1. Which event is the strongest human-navigation candidate, and which headers
   support that conclusion?
2. Why is a link-preview hit not evidence that a person read the document?
3. What could explain a scanner hitting the token repeatedly?
4. What does the token event prove, and what three things does it not prove?
5. How would you preserve the console evidence for an investigation?
6. What alert threshold would you set to avoid paging on routine monitor noise?
