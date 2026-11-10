# CyberChef: Peel Back Two Layers

## Before You Begin

- [ ] You have completed the Base64 and Caesar activities
- [ ] You have the exercise panel open
- [ ] You are comfortable adding more than one operation in CyberChef

!!! note "Order matters"
    A layered message is not automatically more secure. It only asks you to undo
    each simple step in the right order.

## Scenario

The library's partner sent a note that is even less readable than the last one.
The text was shifted, then the shifted text was Base64-encoded.

Use CyberChef to reverse both layers one step at a time. Read the output after
each operation so you can see what changed.

## Walkthrough

### Step 1: Open the message

Open:

```text
http://cyberchef-layers.lab:8080/message.txt
```

Copy the whole line of text.

### Step 2: Start with the outer layer

Open **CyberChef** from the platform menu. Add **From Base64** to the Recipe
column and paste the message into the Input column.

The output should look like ordinary letters, but the words will still be
scrambled. That is the second layer.

### Step 3: Add the second operation

With **From Base64** still in the Recipe, add **ROT13** after it. Read the final
**Output** column.

You should see a normal sentence and a line that starts with
`Training token:`. Copy the `OCR{...}` value into the flag box.

### Step 4: Explain the order

The message was created by shifting the text first and encoding the result
second. To reverse it, undo the encoding first, then undo the shift.

## If You Do Not Have the Lab Browser

Use any browser that can reach the address provided in the exercise. If the
hostname does not resolve, ask your instructor for the address shown in the
exercise panel.

## What Just Happened?

- The message had two reversible layers: a Caesar shift and Base64.
- Undoing the layers in the reverse order recovered the plain text.
- Layered encoding can look impressive, but it does not add real protection.
- Trusted tools help you inspect content without guessing.

## Analysis Questions

**1. Why did the Base64 operation come before ROT13 in the recipe?**

**2. What would happen if you applied the operations in the opposite order?**

**3. Why is layered encoding not the same as layered security?**

**4. What evidence would help you decide whether an unexpected message is genuine?**

**5. What would you do if the decoded message contained real personal data?**
