# Exercise 3.1: Noise in the Nest

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] You can reach `http://portal.lab/`
- [ ] You can reach `http://canary.lab/console`
- [ ] You have `curl` and `python3`

!!! note "Safe target"
    The portal and console are synthetic. The token is lab-owned and the events
    are generated inside the lab network. No external canary service is used.

## Scenario

Northwind Freight published an incident update after a warehouse outage. The
press page links to an incident timeline. Unknown to the publisher, the link is a
canary token managed by the security team.

The console has collected three kinds of automatic traffic: a link-preview bot,
a vulnerability scanner, and an uptime monitor. Your task is to add a
browser-class visit, separate it from the noise, and explain the limits of the
result.

## Your Objectives

- Identify the canary token in the public page without assuming it is a normal download
- Trigger the token from a browser context
- Distinguish a human navigation from automated fetches
- Explain what the alert proves and what it does not
- Capture the flag

## Background: What a Canary Token Is

A canary token is a unique URL, file, or credential that should never be used in
normal work. If it is requested, the defender learns that something reached it.
Common token types include:

| Token type | Example | What it detects |
|---|---|---|
| URL | a unique link in a document | a click, preview, crawl, or scan |
| Image | a 1x1 image in a document | a document opened with image loading enabled |
| File | a document with an embedded URL | a document opened or processed |
| DNS | a unique hostname | a resolver lookup, often from a sandbox |
| Credential | a fake cloud key | an attempt to use a leaked key |

The alert is deliberately simple: timestamp, source address, user agent,
referer, and any fetch metadata. That is enough to triage, but not enough to
attribute.

## Background: Why the Noise Exists

The same public URL can be fetched by many systems:

- **Link previews.** Chat and social apps fetch links to build a card.
- **Scanners.** Vulnerability scanners probe public URLs for known paths.
- **Uptime monitors.** Monitoring services fetch on a schedule.
- **Security products.** Email gateways, proxies, and sandboxes may detonate or
  preview links.
- **Crawlers.** Search engines and archival services index public pages.

A defender who pages on every token hit will quickly learn to ignore the alert.
The skill is triage: which hit is worth preserving and escalating?

## Walkthrough

### Step 1: Inspect the public page

Open `http://portal.lab/` in the lab browser. Read the incident update. The
timeline link is the collection surface.

From a terminal, you can inspect the source without clicking:

!!! kali "Kali - Inspect the public page"
    ```bash
    curl -s http://portal.lab/ | grep -n 'canary.lab'
    ```

The link points at `http://canary.lab/t/incident-timeline`.

### Step 2: Trigger the token from a browser context

Click the timeline link in the lab browser. The canary service records the
request and shows a withdrawn-document page. The link is safe and lab-owned.

If you are working from a terminal, send the headers a browser would send:

!!! kali "Kali - Send a browser-class navigation"
    ```bash
    curl -s -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Dest: document' \
      -H 'Referer: http://portal.lab/' \
      -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36' \
      http://canary.lab/t/incident-timeline
    ```

### Step 3: Read the console

Open `http://canary.lab/console` or fetch the JSON:

!!! kali "Kali - Read the canary events"
    ```bash
    curl -s http://canary.lab/console/api/events | python3 -m json.tool
    ```

The console shows the seeded noise and your live event. The flag appears after a
browser-class hit.

### Step 4: Triage the events

Complete the table in your own notes:

| Signal | Human navigation | Link preview | Scanner | Uptime monitor |
|---|---|---|---|---|
| `User-Agent` | | | | |
| `Referer` | | | | |
| `Sec-Fetch-Mode` | | | | |
| Timing | | | | |
| Confidence | | | | |

Use `observed`, `inferred`, and `unknown` in the confidence column. Do not write
"the attacker" unless another source identifies a person.

### Step 5: Recover the flag

The console shows the lab flag after the browser-class hit. Record it and submit
it on the platform:

> &nbsp;
>
> &nbsp;

## What Just Happened?

You created a canary alert and then did the harder part: triage. The link-preview
bot, scanner, and uptime monitor all prove access to the URL. None of them prove
that a person read the document.

The browser-class event is stronger evidence of a human navigation because it
combines a browser user agent with `Sec-Fetch-Mode: navigate` and a portal
referer. It still does not prove identity or intent. The correct finding is
narrow:

> A browser-class request reached the canary URL at 14:32 UTC from the lab
> network. The user agent and fetch metadata are consistent with a top-level
> navigation. The source address and referer do not identify a person. Further
> corroboration is required.

## Analysis Questions

1. Which event is the strongest human-navigation candidate, and which three
   fields support that conclusion?
2. Why is a link-preview hit not evidence that a person read the document?
3. What could explain a scanner hitting the token repeatedly?
4. What does the token event prove, and what does it not prove?
5. How would you preserve the console evidence for an investigation?
6. What alert threshold would you set to avoid paging on routine monitor noise?
7. How would you explain the finding to a non-specialist without overstating it?

## Defensive Takeaways

- Treat canary tokens as tripwires, not attribution.
- Triage automated traffic before escalating a hit.
- Preserve the raw event and the console export, not just a screenshot.
- Pair the token alert with another source before naming a person or intent.
- Never use a real third-party canary token tied to a personal account in a
  training exercise.
