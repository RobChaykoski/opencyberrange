# Exercise W1.5: Content, Directory, and File Discovery

## Before You Begin

Target: `http://recon.lab/` port `80`. No credentials are required.

This exercise uses **one wordlist**, **one target**, and **one run**. Do not add
extensions, recursion, a larger wordlist, or another host.

## Words to Know

| Term | Meaning |
|---|---|
| **Route** | An application rule that maps a method and path to behaviour. |
| **Directory** | A folder-like path segment, such as `/admin/`. |
| **File** | A named resource, such as `/admin/flag.txt`. |
| **Endpoint** | A specific method-and-path target. |
| **Wordlist** | A file of candidate names. |
| **Extension** | A suffix such as `.php` or `.txt`. This run does not add extensions. |
| **Recursion** | Automatically scanning inside discovered directories. This run does not recurse. |
| **Concurrency** | The number of parallel requests. Gobuster defaults to 10 threads here. |
| **Timeout** | How long a request waits before giving up. |
| **Wildcard response** | A server returning the same page for every path. |
| **Soft 404** | A not-found page returned with a `200` status. |

## Walkthrough

### Step 1: Confirm the target and baseline

```bash
curl -I http://recon.lab/
```

**Expected:** `200 OK` and a normal page. If the target is different, stop.

### Step 2: Run one bounded directory scan

```bash
gobuster dir -u http://recon.lab -w /usr/share/wordlists/dirb/common.txt
```

Record:

- the final progress count (requests attempted);
- the wordlist path;
- the thread count shown in the banner;
- the status codes returned.

Do not press the scan again to “get more.” One run is the limit.

### Step 3: Separate status codes

| Result | Meaning | What to do |
|---|---|---|
| `200` | Resource returned | Validate manually. |
| `301` / `302` | Redirect | Check the `Location` host and path. |
| `403` | Forbidden | Record it; do not bypass. |
| `404` | Not found | Usually hidden by gobuster. |
| Wildcard/soft 404 | Same content for many paths | Stop and treat as false positive. |

### Step 4: Validate representative results

Pick the most relevant results and request them manually:

```bash
curl -I http://recon.lab/admin/
curl -I http://recon.lab/backup/
curl -I http://recon.lab/config/
```

Confirm that the status and content differ from the baseline. Do not request
every discovered path automatically.

### Step 5: Retrieve the lab flag

```bash
curl http://recon.lab/admin/flag.txt
```

Copy the complete `OCR{...}` value into the exercise panel.

## Evidence

| Field | Your note |
|---|---|
| Target | `http://recon.lab/` |
| Wordlist | `/usr/share/wordlists/dirb/common.txt` |
| Threads shown | |
| Requests reported | |
| Discovered paths | |
| Validated paths | |
| False positives | |
| Flag path | `/admin/flag.txt` |
| Confidence | Low / Medium / High |

## Stop Conditions

Stop if:

- the target differs from `recon.lab`;
- the service becomes unstable or returns `429`;
- a redirect leaves `recon.lab`;
- you find personal data or a real-looking credential;
- you are tempted to add extensions, recursion, or a larger wordlist.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| gobuster missing | Ask before installing; do not substitute a public tool. |
| All results are `200` | Check for a wildcard/soft 404. Stop and record it. |
| No interesting paths | Record the result; do not run a different wordlist. |
| `429` | Stop. Do not increase threads or retry rapidly. |
| Flag is 404 | Recheck `/admin/` and the exact path. Do not scan other hosts. |

## What Success Looks Like

You can show the bounded command, the request count, at least one manually
validated path, one false-positive check, and the flag. Submit the lab flag.
