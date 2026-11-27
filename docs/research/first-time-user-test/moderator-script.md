# Moderator script

Read the bold text as written. Do not improvise help.

## Before the timer

**"Thanks for helping. I’m testing the platform, not you. There are no wrong
answers and no penalty for getting stuck. I’ll ask you to think aloud. I may
take notes, but I won’t record your face or voice unless you separately agree."**

**"Please sign this consent form. If you are under 18, your guardian also signs
the guardian section, and I’ll stay in the room the whole time."**

**"You can stop at any time and ask me to delete your notes."**

Confirm the participant has a clean browser profile and no VPN profile.

## Task card

**"You are joining a short cybersecurity course. Starting from this browser with
no account, create an account, join the course with the invite code on the card,
connect the VPN if the exercise asks for it, start the first lab, and submit the
flag. The course card has the invite code and the lab name. Please think aloud
as you go. I will not help unless you are stuck for a while. There is no penalty
for asking; I am testing the platform, not you."**

Hand over the card:

```text
Course: First-Time User Test
Invite code: <test invite code>
Lab: <lab title>
Lab slug: <lab slug>
```

**"When you’re ready, say begin."**

Start the timer.

## Neutral prompts

At 3:00, if the participant has not progressed:

**"What are you trying to do right now?"**

At 7:00, if still stuck:

**"What do you see on the screen?"**

Do not name a control, menu, or step. If the participant asks a direct question,
respond:

**"What would you try next?"**

Record L1 for a neutral prompt. Record L2 if you name a control; L3 if you take
the keyboard.

## Stop

Stop when the platform accepts the flag, or at 15:00, or if the participant is
distressed or raises a privacy concern.

## Debrief

1. **"Walk me through what you did, in your own words."**
2. **"Where did you hesitate or feel unsure?"**
3. **"What did you expect to happen that didn’t?"**
4. **"If you could change one thing, what would it be?"**
5. **"Did anything feel unsafe or unclear about your data?"**

Thank the participant. Do not defend the design.

## Cleanup

- Delete the participant account.
- Revoke the VPN peer.
- Remove the browser profile and downloaded config.
- Store notes under the participant id only.
