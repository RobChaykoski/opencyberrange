# Exercise W1.7: Robots, Sitemaps, JavaScript, and Metadata

## Before You Begin

Target: `http://target.lab/` port `80`. This is a read-only public-metadata
review. No credentials are required.

A path listed in a public file is a **clue**, not permission to access protected
content.

## Words to Know

| Term | Meaning |
|---|---|
| **robots.txt** | A public file that asks crawlers which paths not to visit. |
| **Sitemap** | A public file that lists site pages for crawlers. |
| **Web manifest** | A file describing a web app, such as icons and display settings. |
| **Source map** | A file that maps bundled code back to original source. |
| **JavaScript bundle** | Combined script code delivered by the application. |
| **Comment** | Text in source not displayed by the browser. |
| **API path** | A route intended for application data requests. |
| **Metadata** | Descriptive data, such as titles, authors, or generator tags. |
| **Hidden field** | A form input not shown to the user. |

## Walkthrough

### Step 1: Check robots.txt

```bash
curl -i http://target.lab/robots.txt
```

Record the status and any `Disallow:` or `Allow:` paths. A `404` is a valid
result. A disallowed path is **not** authorisation to access it.

### Step 2: Check sitemap and manifest

```bash
curl -s http://target.lab/sitemap.xml | head -30
curl -s http://target.lab/manifest.json | head -30
```

Record whether each exists and what kind of clue it provides. Do not request
every listed URL automatically.

### Step 3: Inspect the page source

In the RangeBox browser, view the source of `http://target.lab/`. Record:

- the page title;
- generator or framework metadata;
- HTML comments;
- script and stylesheet paths;
- any API path visible in the page.

Do not copy comments containing secrets, internal addresses, or personal data.
Redact them.

### Step 4: Inspect one JavaScript asset

From the source or DevTools, choose one script asset on `target.lab`. Record:

- its path;
- whether a source map is referenced;
- whether the filename suggests a library or application bundle.

Do not download or analyse a public bundle from another host.

### Step 5: Classify each clue

| Clue | Observation | What it suggests | Confidence |
|---|---|---|---|
| robots.txt | | | |
| sitemap.xml | | | |
| manifest.json | | | |
| HTML comment | | | |
| Script path | | | |

## Rules

- Do not access a protected page just because it appears in a public file.
- Do not use a discovered token, key, or password.
- Do not collect more content than the clue requires.
- Do not expand to another hostname.

## Evidence

| Field | Your note |
|---|---|
| URL | `http://target.lab/` |
| robots.txt status | |
| Disallowed paths observed | |
| Sitemap status | |
| Manifest status | |
| Comment/keyword clue | |
| Script path | |
| Source map? | |
| Redactions | |
| Confidence | Low / Medium / High |

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| robots.txt is 404 | Record it; no public robots file exists. |
| Sitemap is 404 | Record it; do not guess another path. |
| Source is hard to read | Use browser search and zoom. |
| A secret appears | Do not copy it. Redact and tell your teacher. |
| A path looks interesting | Do not access it unless the exercise names it. |

## What Success Looks Like

You can show one public metadata clue, one script clue, a confidence statement,
and one sentence explaining why the clue is not permission. This exercise has
**no flag**.
