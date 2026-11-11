# Exercise W1.2: HTTP Request and Response Orientation

## Before You Begin

Use `http://target.lab/` on port `80` for this exercise. It sends one request and
does not modify the application. No credentials are required.

## Words to Know

| Term | Meaning |
|---|---|
| **URL** | The address of a resource, including scheme, host, port, path, and optional query. |
| **Method** | The action requested, such as `GET`, `HEAD`, `OPTIONS`, or `POST`. |
| **Path** | The resource location, such as `/` or `/api/status`. |
| **Query** | Optional `key=value` data after `?` in a URL. |
| **Request header** | Metadata sent by the client, such as `Host` or `User-Agent`. |
| **Request body** | Data sent with methods such as `POST` or `PUT`. |
| **Status code** | A three-digit result code. |
| **Response header** | Metadata returned by the server. |
| **Response body** | The content returned, such as HTML or JSON. |
| **Cookie** | A small key-value record a server asks the browser to store. |
| **Redirect** | A response that points the client to another URL. |

## Walkthrough

### Step 1: Send one annotated request

```bash
curl -v http://target.lab/ -o /dev/null
```

Read the output in this order:

- lines starting with `>` are the request;
- the first request line is method, path, and HTTP version;
- `Host:` selects the virtual host;
- lines starting with `<` are the response;
- the status line is the response result;
- response headers follow the status line;
- the blank line ends the headers;
- the body is omitted here because `-o /dev/null` discards it.

**Expected:** a request line similar to `GET / HTTP/1.1`, a `Host: target.lab`
header, and a status line such as `200 OK`.

### Step 2: Classify the response

| Status | Meaning | Safe interpretation |
|---|---|---|
| `200` | Success | The resource was returned. |
| `301` / `302` | Redirect | The resource moved; check the `Location` host. |
| `401` | Authentication required | A login or token is needed. |
| `403` | Forbidden | The server refused the request. |
| `404` | Not found | The path does not exist, or the server hides it. |
| `429` | Rate limited | Stop and wait; do not increase request rate. |
| `500` | Server error | The application failed; stop and report. |

A status code is an **access result**, not a vulnerability finding.

### Step 3: Check the body separately

```bash
curl -s http://target.lab/ | head -40
```

**Expected:** the first part of the HTML body. Do not paste the whole body into
shared notes. Record only the title and relevant structure.

### Step 4: Note headers that may be inaccurate

Server banners such as `Server:` or `X-Powered-By:` are self-reported. They may
be missing, stale, or deliberately altered. Treat them as clues, not proof.

## Evidence

| Field | Your note |
|---|---|
| URL | `http://target.lab/` |
| Method | `GET` |
| Status | |
| Content-Type | |
| `Server` header | |
| `Location` header | |
| Page title | |
| Observation | |
| Interpretation | |
| Confidence | Low / Medium / High |
| What the response does not prove | |

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| No response | Confirm the lab is running and the target is `target.lab:80`. |
| Redirect to another host | Stop. Do not follow it. |
| `401` or `403` | Do not guess credentials. Record the result and ask. |
| `429` | Stop. Do not retry rapidly. |
| `500` | Stop. Record the result and report it. |

## What Success Looks Like

You can annotate one request-response exchange field by field, classify the
status, and explain why the status or a banner does not prove a vulnerability.
This exercise has **no flag**.
