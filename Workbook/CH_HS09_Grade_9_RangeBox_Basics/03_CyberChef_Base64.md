# CyberChef: Decode a Base64 Message

## Before You Begin

- [ ] You have the exercise panel open
- [ ] You can open the platform menu
- [ ] You know you can use hints at any time
- [ ] You will use only the fictional message in this exercise

!!! note "This is a safe place to start"
    You do not need any prior CyberChef experience. Base64 is an encoding, not a
    secret code. The message and the practice server are fictional.

## Scenario

You are helping at a community library's digital skills desk. A partner
organisation sent a short note about a joint reading program, but the message
arrived as a long string of letters and numbers.

The librarian needs the training token inside the note. Use CyberChef to turn the
message back into readable text.

## Walkthrough

### Step 1: Open the message

In the exercise panel, open:

```text
http://cyberchef-b64.lab:8080/message.txt
```

If you are using the lab browser, the exercise page has an **Open message.txt**
button. Copy the whole line of text.

### Step 2: Open CyberChef

Open the platform menu and choose **CyberChef**. It opens in a new browser tab.
Keep the exercise tab open so you can copy the message.

If your deployment does not show the menu item, open
<https://gchq.github.io/CyberChef/> in a new tab.

### Step 3: Add the decoding operation

In CyberChef, find **From Base64** in the Operations list. Drag it into the
**Recipe** column.

!!! warning "Direction matters"
    Use **From Base64**, not **To Base64**. The note is already encoded. You are
    reversing that encoding.

### Step 4: Read the output

Paste the message into the **Input** column. Read the **Output** column.

You should see an ordinary sentence and a line that starts with
`Training token:`. Copy the `OCR{...}` value into the flag box.

## If You Do Not Have the Lab Browser

You can use any browser on the same network path provided by your instructor.
The target address is `http://cyberchef-b64.lab:8080/message.txt`. If it does not
resolve, ask your instructor for the address shown in the exercise.

## What Just Happened?

- Base64 changes how text is represented; it does not encrypt it.
- **From Base64** reverses that representation and restores the original text.
- CyberChef is a client-side tool: the operations run in your browser.
- Encoded text is still readable by anyone who knows the encoding, so treat it
  as public unless it is protected by real encryption.

## Analysis Questions

**1. Why is Base64 described as encoding rather than encryption?**

**2. What would you check first if the CyberChef output was still unreadable?**

**3. Why should you avoid pasting a real password into a public web tool?**

**4. How could you confirm that the note really came from the partner organisation?**

**5. What is one safe way to share a file that contains real personal data?**
