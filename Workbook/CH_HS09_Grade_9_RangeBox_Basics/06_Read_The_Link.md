# Exercise 1.6: Read the Link Before You Click

## Before You Begin

- [ ] You have the exercise panel open
- [ ] You can open the platform menu and CyberChef
- [ ] You know you can use hints at any time
- [ ] You will use only the fictional message in this exercise
- [ ] You will not click the link

!!! note "You do not need to open the link"
    A URL is text. Reading it is safer than visiting it. In this exercise the
    link uses a reserved `.example` domain, so it cannot reach a real service.

## Scenario

You are volunteering at a community library's digital skills desk. A patron
received an email about a library account check and asks whether the link is
safe. The address looks close to the library's real site, but the patron is not
sure.

The patron does not need to sign in to answer the question. The link itself
contains the evidence. Decode it, read the real host, and recover the training
token from the hidden redirect value.

## Walkthrough

### Step 1: Open the message

In the exercise panel, open:

```text
http://linkcheck.lab:8080/message.txt
```

If you are using the lab browser, the exercise page has an **Open message.txt**
button. Copy the whole message. Do not click the link inside it.

### Step 2: Name the parts of the link

The message contains a link like this:

```text
https://windsorlibrary.example@windosrlibrary-secure.example/verify?next=%2Faccount%2Ftoken%2F...
```

Read it from the scheme to the right:

| Part | Value | What it means |
|---|---|---|
| Scheme | `https` | The connection is encrypted. It does not prove the site is honest. |
| Userinfo | `windsorlibrary.example` | Text before `@`. A browser treats it as a username, not the site. |
| Host | `windosrlibrary-secure.example` | The real destination. Notice the letters `osr`. |
| Path | `/verify` | The page being requested on that host. |
| Query | `next=%2Faccount%2Ftoken%2F...` | Extra data. Percent-encoding hides characters. |

!!! warning "The @ trick"
    Many people read the first familiar-looking domain and stop. The browser
    does not. Everything before the `@` is user information; the host starts
    after it.

### Step 3: Decode the hidden value

1. Open the platform menu and choose **CyberChef**. It opens in a new tab.
2. Find **URL Decode** in the Operations list and drag it into the **Recipe**
   column.
3. Paste the whole message into the **Input** column.
4. Read the **Output** column.

The `%2F` sequences become `/` characters and the `%7B` and `%7D` sequences
become braces.

### Step 4: Read the real destination

Optional: add **Parse URI** after **URL Decode**. Look at the **host** field.
It should show the lookalike host, not the library's real domain.

The decoded `next` value is a path that ends with a training token starting
with `OCR{`. Copy the value inside the braces into the flag box.

### Step 5: Decide what to tell the patron

Before you submit the flag, write one sentence for the patron. It should name
the evidence you used and the safe next step. For example:

> The link only looked like the library because the real host came after an
> `@`. Please do not open it; contact the library through the number on its
> official website.

## If You Do Not Have the Lab Browser

You can decode the message with Python instead of CyberChef:

```bash
curl -O http://linkcheck.lab:8080/message.txt
python3 -c "import urllib.parse; print(urllib.parse.unquote(open('message.txt').read()))"
```

The same rule applies: do not click the link. Read the decoded text.

## What Just Happened?

- A URL has parts. The **host** decides where the browser goes.
- Text before the `@` is user information, not the host. It can be used to make
  a link look like a trusted site.
- Percent-encoding such as `%2F` and `%7B` hides characters until the value is
  decoded.
- `https` protects the connection. It does not tell you who owns the site or
  whether the site is honest.
- A lookalike domain can differ by one letter, one digit, or a swapped pair of
  letters. Read the host slowly.

## A Five-Second Link Check

Use this checklist before you click an unexpected link:

1. **Stop.** Do not click to "see what happens".
2. **Find the host.** Read after the `@` and before the first `/`.
3. **Compare it.** Does it match the organisation's real domain exactly?
4. **Decode it.** Look for percent-encoded redirects and hidden paths.
5. **Verify another way.** Use a phone number or address you already trust, not
   the contact details in the message.
6. **Report it.** Send the message to your instructor or IT contact without
   forwarding the live link.

## Analysis Questions

**1. Which part of a URL decides where the browser goes?**

**2. Why is the text before the `@` not the host?**

**3. What did URL Decode change in the message?**

**4. Why does `https` not prove that a site is safe?**

**5. What would you do instead of clicking the link to check whether the
message is real?**

**6. How could one changed letter in a domain name fool a hurried reader?**

## Accessibility

- Everything in this exercise is text. You can complete it with a keyboard.
- Copy and paste is allowed. You never need to click the link.
- If the platform menu is hidden, use the direct CyberChef address from your
  instructor or the Python command above.
- If you use a screen reader, read the URL one part at a time from the scheme
  to the query string.
