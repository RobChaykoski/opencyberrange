# Exercise W1.8: Forms, Parameters, APIs, and Session Observation

## Before You Begin

Target: `http://api.lab/` port `80`. No credentials are required.

This exercise maps methods and inputs. It does **not** test injection,
credentials, or access-control bypasses. The one `PUT` request writes a benign
test value inside the disposable lab only.

## Words to Know

| Term | Meaning |
|---|---|
| **Query parameter** | Data after `?` in a URL, such as `?id=1`. |
| **Path parameter** | Data inside the path, such as `/users/1`. |
| **Form field** | A named input in an HTML form. |
| **Request body** | Data sent with `POST` or `PUT`. |
| **Header** | Metadata sent with a request or response. |
| **Cookie** | A key-value record stored by the browser. |
| **API endpoint** | A method-and-path interface for application data. |
| **Session** | A server-tracked state associated with a client. |
| **Role** | A permission grouping, such as user or administrator. |
| **Authorisation boundary** | The line between what an identity may and may not do. |

## Walkthrough

### Step 1: Confirm the target

Confirm `api.lab` port `80` in the exercise panel. Stop on any mismatch.

### Step 2: Ask which methods are advertised

```bash
curl -X OPTIONS http://api.lab/ -v
```

**Expected:** an `Allow` header or method list. Record it exactly.

An advertised method is not a vulnerability. It is a capability clue.

### Step 3: Make one read-only GET

```bash
curl -X GET http://api.lab/ -v
```

**Expected:** a normal response and a status such as `200`. Record the content
type and any API hint.

### Step 4: Make one benign PUT

```bash
curl -X PUT http://api.lab/ -v -d "test=data"
```

**Expected:** a response that accepts the test value. This writes only to the
lab's disposable area.

Do not use injection strings, credentials, or destructive methods. Do not send
`DELETE`, `TRACE`, or a mass list of parameters.

### Step 5: Retrieve the lab flag

```bash
curl http://api.lab/uploads/flag.txt
```

Copy the complete `OCR{...}` value into the exercise panel.

### Step 6: Map the input surface

Record what you know without guessing:

| Input | Where | Method | Authentication | Observed response |
|---|---|---|---|---|
| `/` | path | `GET` | None observed | |
| `/` | path | `OPTIONS` | None observed | |
| `/` | path | `PUT` | None observed | |
| `/uploads/flag.txt` | path | `GET` | None observed | |

Do not infer a role or authorization boundary that the lab does not show.

## Evidence

| Field | Your note |
|---|---|
| Target | `http://api.lab/` |
| Allowed methods | |
| GET status | |
| PUT status | |
| Content type | |
| Inputs observed | |
| Authentication observed? | |
| Session/cookie observed? | |
| Confidence | Low / Medium / High |
| What the evidence does not prove | |

## Prohibited

- injection payloads;
- credential guessing;
- access-control bypass;
- mass parameter discovery;
- destructive methods;
- testing another host.

## If You Get Stuck

| Problem | Safe next step |
|---|---|
| OPTIONS is not allowed | Record the status; use GET only. |
| PUT is refused | Record it; do not try another method. |
| Flag path is 404 | Recheck the upload clue; do not scan. |
| A session cookie appears | Do not copy its value. |
| `429` or `500` | Stop and report. |

## What Success Looks Like

You can show the allowed-method result, one GET, one benign PUT, the flag, and a
statement separating capability from authorization. Submit the lab flag.
