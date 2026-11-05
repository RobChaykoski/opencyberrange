# Logging In

Logging in opens your session on the platform. You enter your username and password once, and the platform takes you to your dashboard. Read this page when you are signing in for the first time or troubleshooting a failed attempt.

## Prerequisites

- A registered account that an admin has approved. See [Registering an Account](04_Registering_an_Account.md).
- Your username and password.

## Steps

1. Open the login page at `/login`.
2. Enter your **Username**.
3. Enter your **Password**.
4. Click **Sign In**.

**What you should see:** the platform signs you in and opens your dashboard. Students land on the student dashboard; instructors and admins land on the instructor and admin dashboard.

<figure markdown>

![The login screen with username and password fields and a Sign In button](img/login.png)

<figcaption>The login screen takes a username and password; there is no second authentication step.</figcaption>
</figure>

## Institution sign-in (SSO)

If your institution has enabled OIDC single sign-on, the login page shows one or
more **Sign in with …** buttons above the local form.

1. Select your institution.
2. Sign in on the institution's page, including any MFA it requires.
3. The platform returns you to your dashboard.

SSO-provisioned accounts do not use the local password form. If your account is
pending approval, the platform asks you to contact an administrator. Keep the
local administrator account available as a break-glass path if the identity
provider is unavailable.

## What happens when you sign in

Local login is single factor: a username and a password, with no second step.
SSO may add the institution's own MFA. The platform checks your credentials and
then routes you based on your account state.

```mermaid
flowchart TB
  A[Enter username and password] --> B[Sign In]
  B --> C{Account state}
  C -->|approved and active| D[Open dashboard]
  C -->|not yet approved| E[Account not approved message]
  C -->|inactive| F[Account inactive message]
  C -->|wrong password or locked| G[Incorrect username or password]
  D --> H{Must change password?}
  H -->|yes| I[Go to change password]
  H -->|no| J[Stay on dashboard]
```

If your account is flagged to change its password on first sign-in, the platform sends you to the change-password screen before you reach the dashboard.

## Forgot your username

If you remember the email address on your account but not your username:

1. Open the login page and click **Forgot username?** under the username field.
2. Enter the email address on your account and click **Email my username**.
3. Check that mailbox. The platform sends the username to that address only.

The response is deliberately the same whether or not the address is
registered, so the form cannot be used to discover which emails have accounts.
Mail delivery is best effort: if the administrator has not configured SMTP yet,
the request is accepted but no message is sent. Ask your instructor or
administrator to enable **Admin -> Settings -> Email**.

!!! note
    The username email never contains your password. If you also need a
    password reset, ask an administrator. The platform does not email password
    reset links.

## When sign-in fails

| Message | What it means | What to do |
| --- | --- | --- |
| Incorrect username or password | The username or password is wrong, or the account is locked from too many failed attempts | Re-enter your credentials carefully. If it keeps failing, see [Account Locked](../07_Troubleshooting/02_Account_Locked.md). |
| User account not approved. Please wait for admin approval. | An admin has not approved your account yet | Wait for approval, then sign in. See [Registering an Account](04_Registering_an_Account.md). |
| User account is inactive | An admin has disabled your account | Contact your instructor or admin. |

!!! warning
    A locked account shows the same "Incorrect username or password" message as a simple typo. The platform does not announce a lockout, so if your correct password is being rejected repeatedly, treat it as a possible lockout and see [Account Locked](../07_Troubleshooting/02_Account_Locked.md).

!!! note
    Repeated rapid attempts are rate limited. If you submit too quickly, pause for a minute before trying again.

## After you sign in

Get oriented with the layout: [Navigating the Interface](06_Navigating_the_Interface.md). For more on failed sign-ins, see [Login Issues](../07_Troubleshooting/01_Login_Issues.md).
