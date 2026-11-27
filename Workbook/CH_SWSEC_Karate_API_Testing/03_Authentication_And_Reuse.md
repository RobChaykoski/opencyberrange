# Authenticate Once, Reuse Everywhere

**Lab:** `software-security-3-3-authentication-and-reuse`  
**Time:** about 40 minutes  
**Target:** `http://api.lab:8080`

## Scenario

Northwind's analyst portal now requires a bearer token. The demo account is
`analyst` with password `karate-demo-2026`. The login endpoint returns a token;
the profile endpoint returns the flag only when that token is sent in the
`Authorization` header.

A good suite logs in once, stores the token, and reuses it. A fragile suite logs
in for every scenario and hides failures in repeated setup.

## What you will learn

- send a JSON `POST` from Karate;
- extract a token from the response;
- set an `Authorization` header from a variable;
- reuse a login across scenarios with a called feature and `callSingle`;
- prove the protected endpoint rejects a missing token.

## Step 1 — see the flow with curl

```bash
TOKEN=$(curl -s -X POST http://api.lab:8080/api/v1/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"analyst","password":"karate-demo-2026"}' | jq -r .token)

curl -s -H "Authorization: Bearer $TOKEN" http://api.lab:8080/api/v1/me
curl -s http://api.lab:8080/api/v1/me
```

The first profile call returns the analyst record and the flag. The second
returns `401` because no token was sent.

## Step 2 — write a reusable login feature

Create `features/login.feature`:

```gherkin
Feature: Northwind login helper

  Scenario: obtain an analyst token
    * url 'http://api.lab:8080'
    * path 'api/v1/login'
    * request { username: 'analyst', password: 'karate-demo-2026' }
    * method post
    * status 200
    * match response.token == '#string'
    * def token = response.token
```

The called feature returns its variables to the caller. `auth.token` is the
token.

## Step 3 — call it once and reuse it

Create `features/profile.feature`:

```gherkin
Feature: Northwind analyst profile

  Background:
    * def auth = karate.callSingle('login.feature')
    * url 'http://api.lab:8080'
    * header Authorization = 'Bearer ' + auth.token

  Scenario: the profile returns the analyst and the flag
    * path 'api/v1/me'
    * method get
    * status 200
    * match response.username == 'analyst'
    * match response.role == 'analyst'
    * match response.flag == '#string'

  Scenario: the profile rejects a missing token
    * header Authorization = null
    * path 'api/v1/me'
    * method get
    * status 401
```

`karate.callSingle` caches the result for the whole run, so the login happens
once even when the suite has many scenarios. If your runner cannot resolve the
path, use the same path style as your `read` calls (`classpath:login.feature`
in a Maven layout, or the relative file path in a standalone layout).

## Step 4 — run it

```bash
java -jar karate.jar features/profile.feature
```

You should see two scenarios pass. The negative scenario is not optional: it
proves the endpoint actually enforces the token instead of only accepting one.

## Step 5 — capture the flag

The `/api/v1/me` response contains the `flag` field. Submit it on the lab page
after both scenarios pass. Do not copy the token or the flag into a shared
document.

## Step 6 — explain the trade-off

Answer:

1. What would happen if every scenario logged in again?
2. Why is a cached token useful in a test run, and why is it risky in a
   long-lived shared environment?
3. Where should a test token come from in a real CI pipeline?

## Evidence to submit

- `features/login.feature`
- `features/profile.feature`
- the run summary showing the positive and negative scenarios
- a short note on where the token is stored and why it is not committed

## Defensive takeaway

Treat tokens as credentials: keep them out of logs, scope them to the task, and
expire them. Test both the positive path and the missing-token path. A login
helper is shared infrastructure; make it obvious where the credential comes
from and never hard-code a production token in a test file.
