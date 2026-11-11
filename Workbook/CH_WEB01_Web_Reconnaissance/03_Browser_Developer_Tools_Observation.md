# Exercise W1.3: Browser Developer Tools Observation

## Before You Begin

Use the RangeBox browser and `http://target.lab/`. This is **passive observation**.
Do not edit or replay requests, execute console code, or change application state.

## Words to Know

| Term | Meaning |
|---|---|
| **Network panel** | Shows requests the browser made and their responses. |
| **Elements panel** | Shows the page structure and styles. |
| **Sources panel** | Shows HTML, JavaScript, and source files the browser loaded. |
| **Application / Storage panel** | Shows cookies, local storage, session storage, and related data. |
| **Console** | Shows page messages and allows scripts. This exercise does not run code there. |
| **Timing** | When a request started and how long it took. |
| **Initiator** | What caused a request, such as a page load or a script. |
| **Content type** | The declared format of a response, such as HTML, JSON, or JavaScript. |
| **Response preview** | A browser-rendered view of response content. |
| **Source map** | A file that maps bundled code back to original source files. |

## Walkthrough

### Step 1: Open the page with DevTools closed

Open `http://target.lab/` normally. Record the title and visible purpose.

### Step 2: Open Developer Tools

Use the browser menu or `F12` / `Ctrl` + `Shift` + `I`. Keep the page unchanged.

### Step 3: Observe the Network panel

Reload the page once. Record:

- the document request (`/`);
- CSS, JavaScript, image, and font requests;
- status codes;
- content types;
- initiators;
- whether any request goes to another hostname.

**Stop if:** a request goes to a public domain or a host outside `target.lab`.

### Step 4: Observe Elements and Sources

- Confirm the document title.
- Look at the HTML structure and any comments.
- In Sources, identify bundles and whether source maps exist.
- Do not open or copy secrets. If a token or personal data appears, redact it.

### Step 5: Observe Application or Storage

Record:

- cookie names and attributes (`Secure`, `HttpOnly`, `SameSite`, expiry);
- whether local storage or session storage contains data;
- whether any value looks like a credential or personal information.

Do not copy values. Record only the key name and whether the value is sensitive.

## Evidence

| Field | Your note |
|---|---|
| URL | `http://target.lab/` |
| Page title | |
| Document request status | |
| Number of requests | |
| Third-party hosts | |
| Cookie names | |
| Cookie attributes observed | |
| Storage keys observed | |
| Sensitive values found? | Yes / No / Unsure |
| Observation | |
| Interpretation | |
| Confidence | Low / Medium / High |

## Prohibited in This Exercise

- editing or replaying a request;
- running JavaScript in the Console;
- copying cookies, tokens, or personal data;
- uploading page content to a third-party tool.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| Network is empty | Reload once. |
| Too many requests | Filter to Document or XHR/Fetch. |
| Another host appears | Stop and ask; do not follow it. |
| A token is visible | Do not copy it. Record the key name only. |
| DevTools is hard to read | Use browser zoom and keyboard navigation. |

## What Success Looks Like

You can describe the document request, one script or style request, the cookie
attributes, and one storage key without copying a sensitive value. This exercise
has **no flag**.
