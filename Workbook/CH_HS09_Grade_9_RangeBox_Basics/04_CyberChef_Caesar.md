# Exercise 1.4: CyberChef: Read a Caesar Shift

## Before You Begin

- [ ] You have completed the Base64 activity or know how to open CyberChef
- [ ] You have the exercise panel open
- [ ] You know you can use hints at any time

!!! note "A simple cipher is still a cipher"
    A Caesar shift moves each letter a fixed number of places through the
    alphabet. It is easy to try every possible shift, so it does not protect a
    real secret.

## Scenario

The community library's partner sent another short note. This time the letters
have been shifted through the alphabet instead of encoded with Base64.

The librarian needs the training token to confirm the next booking. Use CyberChef
to reverse the shift and read the original message.

## Walkthrough

### Step 1: Open the message

Open:

```text
http://cyberchef-rot.lab:8080/message.txt
```

Copy the whole line of text.

### Step 2: Open CyberChef

Open the platform menu and choose **CyberChef**. Keep the exercise tab open.

### Step 3: Try ROT13

Find **ROT13** in the Operations list and drag it into the **Recipe** column.
Paste the message into the **Input** column.

ROT13 is a Caesar shift of 13 places. Applying it twice returns the original
text, which is why it is its own inverse.

### Step 4: Read the output

Read the **Output** column. You should see an ordinary sentence and a line that
starts with `Training token:`. Copy the `OCR{...}` value into the flag box.

If ROT13 does not work, replace it with **Caesar Brute Force** and look for the
candidate that reads like a normal message.

## If You Do Not Have the Lab Browser

Use any browser that can reach the address provided in the exercise. If the
hostname does not resolve, ask your instructor for the address shown in the
exercise panel.

## What Just Happened?

- A Caesar shift changes each letter by a fixed number of places.
- ROT13 is a shift of 13 and is easy to reverse.
- A brute-force view shows every possible shift so you can recognise the
  readable candidate.
- A simple shift is not suitable for protecting real information.

## Analysis Questions

**1. What stays the same when a message is shifted with a Caesar cipher?**

**2. Why is ROT13 easy to reverse without a key?**

**3. If the message used a shift other than 13, how would CyberChef help you find it?**

**4. Why is a Caesar shift a poor choice for protecting a real password?**

**5. What should you do before acting on an unexpected encoded message?**
