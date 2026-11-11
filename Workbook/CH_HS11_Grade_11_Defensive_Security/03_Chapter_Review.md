# Chapter Review — Stage 3: Defensive Evidence

## What You Practised

- Reading a web server access log
- Comparing successful and failed requests
- Spotting repeated probing from one source address
- Explaining evidence without guessing beyond it

## Check Your Understanding

**1.** What does a `404` status code mean in an access log?

**2.** Why can repeated `404` requests from one address be suspicious?

**3.** What is the difference between finding a suspicious line and proving what
an attacker did?

**4.** Why should a defender avoid publishing a log that contains real IP
addresses, usernames, or personal information?

## Command Cheat Sheet

| Command | What it does |
|---|---|
| `curl http://logs.lab:8080/access.log` | Print the access log |
| `curl ... -o access.log` | Save the log to a file |
| `grep " 200 " access.log` | Show successful requests |
| `grep " 404 " access.log` | Show requests the server could not find |
| `grep "<address>" access.log` | Show activity from one source |
| `grep "OCR{" access.log` | Find training-token text |

## Key Takeaways

- Logs are evidence, not conclusions.
- Status codes and paths are a quick way to find the interesting lines.
- A pattern of failures followed by an unexpected success is more meaningful than
  any single request.
- Defensive security includes protecting the evidence itself and the people it
  describes.

## Where Next?

Stage 4 applies these investigation habits to a browser-only community event
challenge. You will inspect a fictional conference portal, check where a file came
from, and protect the people whose information appears in it.

## Free practice and certification next steps

These optional free resources match this chapter. They do not replace the
lab or this workbook.

- **Cisco NetAcad** — free networking and cybersecurity foundations: <https://www.netacad.com/>
- **TryHackMe** — beginner-friendly guided rooms: <https://tryhackme.com/>
- **CyLab Security Academy** — free CTF-style cybersecurity learning: <https://learn.cylabacademy.org/>
- **ISC2 Certified in Cybersecurity** — free entry-level training and exam pathway: <https://www.isc2.org/landing/1mcc>

See [Free training and certifications](../FREE-TRAINING-AND-CERTIFICATIONS.md)
for the full map and the privacy note.
