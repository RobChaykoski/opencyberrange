# High School Cybersecurity — Grade 10 RangeBox Basics

## Welcome

In Grade 9 you learned to move around the RangeBox desktop. This chapter adds
the network view: how a name becomes an address, how a browser asks a server for
a page, and how to read the response.

You still do not need to install anything. The activities work in RangeBox, and
the lab browser is available as a fallback.

## What You Need

- A browser
- The exercise panel open in SWOCTS Cyber Range
- A RangeBox desktop, or the lab browser as a fallback

## Four Ideas to Carry Forward

### 1. A hostname is a name

`network.lab` is a hostname. It is easier to remember than a number. The lab
network resolves that name to the target container for you.

### 2. A URL has parts

```text
http://network.lab:8080/status.json
```

- `http` is the scheme.
- `network.lab` is the host.
- `8080` is the port.
- `/status.json` is the path.

### 3. A response has more than a body

A web response includes:

- a status line, such as `HTTP/1.1 200 OK`;
- headers, such as `Content-Type` and `X-OCR-Token`;
- a blank line;
- the body.

The body is what the page shows. The headers are the part people often forget
to read.

### 4. A message is more than its body

An email carries routing and authentication headers that a mail app hides. The
raw message records where it came from, which servers relayed it, and what the
receiver's checks said. Reading those headers is the same skill as reading an
HTTP response, applied to a message.

## Activities

1. [RangeBox Network Basics](01_Network_Basics.md)
2. [RangeBox Browser and Source](02_Browser_and_Source.md)
3. [Dissect an Email](03_Email_Metadata.md)
4. [MFA and the Lost Phone](04_MFA_Lost_Phone.md)

## Safety Reminder

Every target in this chapter is fictional and isolated. You cannot affect
anything outside the lab. Using hints is allowed, and you can stop at any time.
