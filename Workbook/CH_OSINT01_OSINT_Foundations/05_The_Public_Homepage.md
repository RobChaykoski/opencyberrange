# Exercise 2.2: The Public Homepage

## Before You Begin

- [ ] You can reach the offline mirror at `http://connect.lab:8080`
- [ ] You have `curl` and `grep`

## Scenario

SWOCTS Hub is a public community homepage. Like any modern site, it ships
metadata and source code to every visitor. This exercise uses a reviewed
offline mirror as the assessed target. The live page is retired from the lab;
the mirror is authoritative for the flag and the automated checks.

A flag has been placed in the mirror's source for this exercise. The rendered
page looks ordinary; the flag is in the document metadata. No personal data is
collected.

## Your Objectives

- Treat a public homepage as an OSINT source
- Inventory author, generator, keywords, Open Graph, Twitter card, and custom metadata
- Explain what each metadata field reveals to an outsider
- Decide which metadata field provides the most useful information
- Record the exact URL and source location of the finding

## Background: The Head Is Part of the Page

A modern homepage is more than its visible text. The document `<head>` can
contain:

- `<title>` and description metadata
- social-sharing cards (`og:` and `twitter:` tags)
- framework build identifiers
- custom `meta` tags used by internal tools
- analytics and verification tokens

Most visitors never see the head. An OSINT researcher reads it.

## Walkthrough

### Step 1: Open the mirror

Open:

```text
http://connect.lab:8080
```

Use **View Page Source** (not the browser's rendered text view).

If you are an adult learner and the live page is available, you may compare it
read-only at `https://www.swocts.com/`. Do not interact with the site or collect
personal data.

### Step 2: Fetch the source

```bash
curl -s http://connect.lab:8080/ -o swocts.html
```

### Step 3: Build a metadata inventory

Do not search only for the flag. List every field, then decide which field is
most useful to an outsider:

```bash
grep -iE '<title|<meta' swocts.html
```

Complete the inventory:

| Field | Example value | What it reveals |
|---|---|---|
| `author` | SWOCTS Community Team | Who maintains the page, or the team name |
| `generator` | Hugo 0.125.7 | The build tool and version, which narrows known issues |
| `keywords` | cybersecurity, community, workshops | The site's topics and audience |
| `og:title` / `og:description` | SWOCTS Hub / Free community events | What social platforms display when the link is shared |
| `og:image` | `/images/hub-cover.png` | A public asset path and image metadata |
| `twitter:card` | `summary_large_image` | The social-preview format |
| `x-swocts-osint` | `OCR{...}` | A deliberate custom marker; the flag is here |

Then answer: **which metadata field reveals the most useful information?**

There is no single correct answer. A generator version can narrow known
vulnerabilities; an author field can identify a team; a custom tag can expose an
internal marker. The skill is to inventory the fields and justify the priority.

### Step 4: Submit the flag

Copy the `OCR{...}` value into the exercise flag box. Record the URL and the
exact tag you found so another analyst can reproduce the finding.

## What Just Happened?

The site owner left a marker in the public source. This is not a
vulnerability; it is a deliberate OSINT breadcrumb. The lesson is that the
public surface includes metadata, comments, and build artifacts that never
appear in the visible page.

The same technique applies to any public site: fetch the source, read the
head, and search for identifiers that should not be there.

## Analysis Questions

**1. Which metadata field revealed the most useful information, and why?**

**2. What does the `generator` field tell an outsider?**

**3. How can Open Graph or Twitter card data expose internal context?**

**4. Which fields would you remove before publishing the page?**

**5. What kinds of real secrets are sometimes leaked in page metadata?**

**6. How would you archive the page so the finding is reproducible after the site changes?**

**7. How would you report a real metadata leak without publishing the secret?**

## Defensive Takeaways

- Treat metadata as public content and review it before launch.
- Strip internal build identifiers and staging markers from production.
- Do not put secrets in `meta` tags, comments, or source maps.
- Include the document head in launch checklists and security reviews.
- Monitor public source changes if your site is a high-value target.

## If You Get Stuck

- Make sure you are looking at the source, not the rendered text.
- Search for `OCR{`, `osint`, or `meta name`.
- If the live site is blocked, use the mirror at `http://connect.lab:8080`.
- The flag is in a custom `meta` tag in the head.
