# Registering an Account

Registration creates your student account. You fill in a short form, the platform creates the account, and an admin approves it before you can log in. Read this page when you are signing up for the first time.

## Prerequisites

- A running platform you can reach in your browser. See [System Requirements](02_System_Requirements.md).
- An email address and a username you want to use.

## What registration involves

Registration is open: anyone who can reach the platform can submit the form. Every account is then held for admin approval before it can sign in. There is no invite code for the platform account, no email-verification step, and no second authentication factor.

```mermaid
flowchart TB
  A[Open /register] --> B[Fill the form]
  B --> C[Create Account]
  C --> D[Account created, pending approval]
  D --> E[Admin approves the account]
  E --> F[You can log in]
```

## Steps

1. Go to the login page and click **Register here**, or open `/register` directly.
2. Enter your **Username**. It must start with a letter and may contain letters, numbers, underscores, and hyphens, between 3 and 50 characters.
3. Enter your **Email** address.
4. Leave **Email me a registration confirmation** unchecked unless you want a receipt. This is optional and is not account verification.
5. Optionally enter a **First name** and **Last name**. They appear on completion certificates and can be changed later in your profile.
6. Enter a **Password**. The help text reads: must be at least 8 characters and contain uppercase, lowercase, and a number. The form checks each field as you leave it.
7. Re-enter the same password in **Confirm Password**.
8. Select your **Age group**. This sets the privacy defaults; the platform does not collect your date of birth.
9. Check the **Privacy notice** acknowledgement. If you are under 13, an instructor must record a parent or guardian consent reference before an institution-managed account is created.
10. Click **Create Account**.

**What you should see:** a success message that reads, "Account created successfully! Your account is pending administrator approval. You will be able to log in once approved." The page then sends you back to the login screen after a few seconds.

<figure markdown>

![The registration form with username, email, password, and confirm password fields](img/register.png)

<figcaption>The registration form collects a username, email, password, age group, and privacy acknowledgement; names are optional and there is no invite code or email-verification step.</figcaption>
</figure>

## Approval (on by default)

By default a freshly registered account is held for approval until an admin approves it, and you cannot log in during that wait; no verification email is sent. An administrator can turn approval off in platform settings, in which case new accounts are approved automatically and can sign in immediately. If you are unsure which mode your instance uses, ask your administrator.

!!! note
    If you try to log in before an admin approves you, the platform tells you the account is not yet approved. Contact your instructor or admin if the wait is longer than expected.

!!! warning
    If your chosen username, email, or student ID already belongs to an account, the platform returns a single generic message: "An account with these credentials already exists." The message does not say which field collided, so try a different username and email.

## After you are approved

Once an admin approves your account, sign in: [Logging In](05_Logging_In.md). If your first sign-in fails, see [Login Issues](../07_Troubleshooting/01_Login_Issues.md).
