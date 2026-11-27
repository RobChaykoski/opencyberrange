# Negative Tests and Evidence Reports

**Lab:** `software-security-3-4-negative-tests-and-evidence`  
**Time:** about 45 minutes  
**Target:** `http://api.lab:8080`

## Scenario

Northwind's account endpoint is supposed to return only the signed-in user's
account. The analyst account owns account `1001`. Account `1002` belongs to a
manager and should return `403`.

The service has a broken object level authorization (BOLA) check. Your job is to
write the test that *should* pass, run it, and explain why the failure is a real
finding rather than a broken test. The flag is in the response the service
should never have returned.

## What you will learn

- write a negative test that expects `403`;
- distinguish a failing test from a failing service;
- tag security checks and run them as a separate suite;
- produce a finding with reproducible evidence and a control change.

## Step 1 — read your own account

```bash
curl -s http://api.lab:8080/api/v1/accounts/1001
```

You should see the analyst's account. Now request the manager's account:

```bash
curl -s http://api.lab:8080/api/v1/accounts/1002
```

The correct response is `403`. The actual response is `200` with the other
account's data. That is the bug.

## Step 2 — write the test you expect to pass

Create `features/accounts.feature`:

```gherkin
Feature: Northwind account authorization

  @security @bola
  Scenario: another user's account is forbidden
    * url 'http://api.lab:8080'
    * path 'api/v1/accounts/1002'
    * method get
    * status 403

  @security @not-found
  Scenario: a missing account returns 404
    * url 'http://api.lab:8080'
    * path 'api/v1/accounts/9999'
    * method get
    * status 404
```

Run it:

```bash
java -jar karate.jar -t @security features/accounts.feature
```

The first scenario fails with `status code was: 200, expected: 403`. Do not
change the expectation. The failure is the evidence. The second scenario
passes and proves the endpoint distinguishes a missing object from a forbidden
one.

## Step 3 — capture the flag

The leaked account response contains the `flag` field. Submit it, then keep the
failing run report. The flag alone is not the finding.

## Step 4 — write the finding

Use this structure:

| Field | Value |
|---|---|
| Finding ID | NW-2026-001 |
| Title | Broken object level authorization on `/api/v1/accounts/{id}` |
| Asset | `http://api.lab:8080` |
| Identity | `analyst` (owns account 1001) |
| Request | `GET /api/v1/accounts/1002` |
| Expected | `403 Forbidden` |
| Observed | `200 OK` with the manager account and the flag |
| Evidence | `accounts.feature`, `target/karate-reports/karate-summary.html` |
| Impact | Any authenticated analyst can read another user's account balance |
| Control change | Authorize the object against the authenticated subject, add a regression test for `403`, and log cross-account reads |
| Owner | Accounts API team |
| Due | Next release gate |

## Step 5 — run the evidence report

```bash
java -jar karate.jar -t @security -o target/security-run features/
```

Open `target/security-run/karate-reports/karate-summary.html`. The report shows
the failing scenario, the request, the response, and the assertion. Attach the
report or its path to your submission.

Answer:

1. Why is `200` on a foreign object worse than a `500`?
2. What is the difference between authentication and authorization here?
3. Which control would have prevented the leak, and where would you test it
   next?

## Evidence to submit

- `features/accounts.feature` with both negative scenarios
- the failing report from the tagged run
- the completed finding table
- a one-sentence explanation of why the test must not be weakened

## Defensive takeaway

Authorize every object read against the authenticated subject, not just the
object id. Prefer a server-side ownership check or a policy layer over a
client-supplied role. Add a regression test that expects `403` for a foreign
object, and make the test part of the release gate.
