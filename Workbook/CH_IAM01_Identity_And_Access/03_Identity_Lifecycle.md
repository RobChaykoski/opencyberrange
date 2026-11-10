# Identity Lifecycle: Joiners, Movers, and Leavers

## Before You Begin

- [ ] You have completed **OAuth and OpenID Connect**
- [ ] You have the exercise panel open
- [ ] You can open the directory and test an API token
- [ ] You will use only the fictional accounts in this lab
- [ ] You will not test a real token or account

!!! note "Access does not expire by itself"
    An account that is no longer needed still works until someone disables it.
    Tokens are often forgotten because they do not look like user accounts.

## Scenario

A community centre is overdue for its quarterly access review. The volunteer
coordinator left 14 months ago. The account was never disabled, and the API
token was never revoked.

The directory shows current accounts, roles, last login dates, tokens, and
scopes. Your job is to find the account that should have been removed, test its
access, recover the training token, and write the offboarding fixes.

## Background

Identity lifecycle work is usually described as **joiner, mover, leaver**:

| Stage | What should happen |
|---|---|
| **Joiner** | Create the account, assign the minimum role, enroll MFA, and record an owner. |
| **Mover** | Remove old access, grant new access, and review shared resources. |
| **Leaver** | Disable the account, revoke tokens and sessions, transfer ownership, and record the review. |

Two related ideas matter here:

- **Least privilege:** an account should have the access its current job needs,
  not every permission it has collected.
- **Access review:** a scheduled check that every account, role, token, and
  service identity still has a current owner and a reason to exist.

Service accounts are easy to forget because no person signs in to them. Give
each one a named owner, a documented purpose, a minimal scope, and a rotation
plan.

## Walkthrough

### Step 1: Open the directory

Open:

```text
http://identity-life.lab:8080/directory
```

The table shows each account's user, role, status, last login, API token, and
scope.

### Step 2: Find the account that should not be active

Compare `status` with `last_login`. One account is still **active** but has not
signed in for more than a year. That is the leaver.

The same account has the `reports:admin` scope. A volunteer who left should not
still hold an administrator token.

### Step 3: Test a read-only token

Use the form on the access-review page, or:

```bash
curl -s 'http://identity-life.lab:8080/api/reports?token=tok_amara_staff_2b7c'
```

The endpoint returns **403**. The token has `reports:read`, but the export
requires `reports:admin`.

### Step 4: Test the stale admin token

Use the token from the leaver account:

```bash
curl -s 'http://identity-life.lab:8080/api/reports?token=tok_rowan_9f2c'
```

The export opens and contains the training token. Copy the `OCR{...}` value into
the flag box.

### Step 5: Write the offboarding fix

Write a short checklist for the coordinator:

```text
1. Disable the account on the last working day.
2. Revoke API tokens, sessions, and refresh tokens.
3. Transfer files, mailboxes, and shared-drive ownership.
4. Remove group and application access.
5. Record the review and the date.
```

## What Just Happened?

- The account was never disabled, so it remained a valid identity.
- The token was never revoked, so it still worked without a person signing in.
- The account held more access than the role needed.
- The quarterly review did not catch the gap.
- The 403 versus 200 response showed the difference between read and admin
  scope.

## The Fixes

| Problem | Fix |
|---|---|
| Leaver account remains active | Trigger offboarding from the HR or roster event, not from a reminder |
| Token still valid | Revoke all credentials and sessions as part of offboarding |
| Excess privilege | Assign the minimum scope and review it when the role changes |
| Shared credentials | Give each service a named owner and a unique credential |
| Review missed the gap | Run scheduled access reviews with a named reviewer and evidence |
| No record | Keep the review date, decision, and owner for audit |

## Analysis Questions

**1. Why is a disabled account not enough if its API token still works?**

**2. What is the difference between a user account and a service account?**

**3. Which account in the directory should have been removed, and what evidence
supports that?**

**4. Why did the read-only token return 403 instead of 200?**

**5. What should happen to a leaver's files and shared drives?**

**6. How would you prove that an access review actually happened?**

**7. What would you check first if a former employee's token appeared in a log?**

## Accessibility

- The directory is a table. Read one column at a time if it is wide.
- The token can be copied from the table or tested with the form; a terminal is
  optional.
- All commands are plain text and work with a keyboard.
- If the table is difficult to read with a screen reader, ask for the directory
  as a list of accounts with one field per line.
