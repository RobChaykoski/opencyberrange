# Exercise 2.4: MFA and the Lost Phone

## Before You Begin

- [ ] You have the exercise panel open
- [ ] You can open the staff portal and the staff directory
- [ ] You know you can use hints at any time
- [ ] You will use only the fictional demo account
- [ ] You will not enter a real password, recovery answer, or authenticator code

!!! note "Recovery is part of MFA"
    A second factor only helps if the recovery path is at least as strong as the
    factor it replaces. A security question that anyone can answer from a public
    profile turns MFA into a formality.

## Scenario

A community centre volunteer lost their phone on the way to the Tuesday
reading circle. The staff account uses a password and an authenticator app. The
volunteer needs to get back in today.

The portal offers a recovery question. Your job is to follow the recovery path,
recover the training token, and explain why the second factor did not protect
the account.

## Background

| Method | Strength | Main weakness |
|---|---|---|
| SMS code | Weakest common factor | SIM swap and interception |
| Authenticator app (TOTP) | Better; works offline | Phone loss, backup and recovery |
| Hardware key / passkey | Strongest common factor | Device loss, enrollment and recovery |

The order matters: a strong factor with a weak recovery question is only as
strong as the question. A recovery answer that is public, guessable, or stable
for life is a password reset waiting to happen.

## Walkthrough

### Step 1: Sign in with the demo account

Open the exercise page and choose **Open the staff sign-in**. Use:

```text
amara / Library2026!
```

The password is accepted. The portal then asks for a six-digit authenticator
code.

### Step 2: Notice the block

The volunteer's phone is lost, so there is no code to enter. The page offers
**Use account recovery**. That is the path an attacker would also try.

### Step 3: Read the recovery question

Open the recovery form. It asks for the account username and a favourite book.
The answer is not a secret if the organisation publishes staff profiles.

### Step 4: Check the public staff directory

Open the staff directory and read Amara's profile. The favourite book is listed
there. This is the same information a stranger could find.

### Step 5: Recover the account

Submit the username and the book title. The recovery flow resets MFA and shows
the training token. Copy the `OCR{...}` value into the flag box.

### Step 6: Write the lost-phone plan

Write five steps the centre should follow when a volunteer loses a phone:

1. Revoke the old sessions.
2. Re-enroll MFA on the new device.
3. Use a pre-generated recovery code or a second enrolled authenticator.
4. Notify the account owner and the coordinator.
5. Record the event and check for unusual sign-ins.

## What Just Happened?

- The account had a strong second factor, but the recovery path bypassed it.
- The recovery answer was published on a public profile.
- MFA protects a sign-in event; recovery protects the account when the factor is
  unavailable. Both need design.
- A security question is not a secret when the answer is part of a public bio.

## The Fixes

| Problem | Fix |
|---|---|
| Public recovery answer | Use pre-generated recovery codes or a second enrolled authenticator |
| Codes stored in the same account | Store them offline, in a password manager or a sealed envelope |
| Recovery bypasses MFA | Require a second channel or an administrator-approved reset |
| No alert after recovery | Notify the account owner and revoke old sessions |
| No recovery plan | Document the lost-phone steps before an incident |

## Analysis Questions

**1. Why is a public favourite book a weak recovery answer?**

**2. Which MFA method would you recommend for a volunteer account, and why?**

**3. What should happen to old sessions after a recovery?**

**4. Why is MFA not “set and forget”?**

**5. What would you check in the sign-in logs after a recovery event?**

**6. How could the centre test its recovery plan without exposing a real
account?**

## Accessibility

- The portal and directory are text pages. You can complete the exercise with a
  keyboard.
- The recovery form accepts copy and paste; use the exact book title from the
  profile.
- If the sign-in form is difficult to use, ask your instructor for the recovery
  path directly.
- Never use a real authenticator code or personal recovery answer in a lab.
