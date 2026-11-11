# Internet and Network Basics

This extra practice activity introduces the words you will see in later network
labs: network, host, client, server, IP address, hostname, protocol, service,
port, request, and response.

You will not scan, probe, or attack anything. You will make **one read-only
request** to the assigned practice target and read the connection details.

## Before You Begin

Complete [Terminal Foundations](03_Terminal_Foundations.md) first. You should
already have the RangeBox terminal open.

### Where to run this activity

| Place | What it is | Used in this activity? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only to view the OpenCyberRange page in your browser. |
| **Web browser** | The app that shows the OpenCyberRange page and the RangeBox desktop. | Yes, to view the exercise. |
| **OpenCyberRange page** | The platform page that opens the exercise. | Yes, to launch the exercise. |
| **RangeBox desktop** | The remote Linux desktop provided by the platform. | Yes. This is your practice workstation. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run the command here.** |
| **Assigned target** | The practice server `rangebox.lab:8080`. | **Yes. This is the only network system you may contact.** |
| **Public internet** | Real websites and services outside the lab. | **No. It is out of scope for this activity.** |

!!! warning "Only the assigned target"
    Use only the target shown in your exercise. In this activity the target is
    `rangebox.lab:8080`. Do not contact public websites, your school network,
    another student's lab, or any other address. Do not use network scanning
    tools or try other ports. If you are unsure, stop and ask your teacher.

### What you need

- [ ] The RangeBox terminal open.
- [ ] An exercise that includes the target `rangebox.lab:8080`.
- [ ] A notes file for the command and output.
- [ ] About **15–20 minutes**.

If your exercise does not include `rangebox.lab:8080`, ask your teacher for the
correct practice target. Do not use a real website instead.

### What you will be able to do

By the end of this activity, you will be able to:

- explain what a network, host, client, server, IP address, hostname, protocol,
  service, port, request, and response are;
- explain why a port is a number, not a physical opening;
- read the parts of a URL;
- tell the student device, the OpenCyberRange page, RangeBox, the assigned
  target, and the public internet apart;
- make one safe request to the assigned target and explain what happened;
- recognise a name-resolution failure and a connection failure.

## Words to Know

Read this table before you start. Every term is used in the activity.

| Term | What it means |
|---|---|
| **Network** | Two or more devices that can send data to each other. |
| **Host** | Any device on a network with an address. A host can act as a client, a server, or both. |
| **Client** | A device or program that asks for data or a service. Your browser is often a client. |
| **Server** | A device or program that provides data or a service to a client. |
| **IP address** | A number-based address of a host on a network, such as `192.0.2.10`. The example is for teaching only; it is not your target. |
| **Hostname** | A human-readable name that maps to an IP address, such as `rangebox.lab`. |
| **DNS** | The naming system that maps a hostname to an IP address, like a contact list for computers. DNS stands for Domain Name System. |
| **Protocol** | An agreed set of rules for communication. HTTP is the protocol used for ordinary web pages. |
| **HTTP** | The protocol for requesting and sending web pages. It is not encrypted. |
| **HTTPS** | The protected version of HTTP. The data is encrypted so others cannot easily read it. |
| **Service** | A program on a server that provides something, such as a web page. |
| **Port** | A number that identifies which service on a host should receive a request. A port is **not** a physical opening. |
| **Request** | The message a client sends to ask for something. |
| **Response** | The message a server sends back. |
| **URL** | A web address that names a protocol, host, optional port, and path. |
| **Localhost** | A special hostname that means "this computer". Web developers often use it for a local test server, such as `http://localhost:3000`. |
| **Public internet** | Real websites and services outside the practice lab. It is out of scope here. |

## A Diagram in Words

The diagram below shows the path from your device to the practice target. It is
text, not a picture, so it works with a screen reader and with zoom.

```text
[Student device]
  browser
     |
     |  opens the OpenCyberRange page
     v
[OpenCyberRange platform]
     |
     |  launches the exercise
     v
[RangeBox desktop]
  terminal
     |
     |  one request to the assigned target
     v
[Assigned target: rangebox.lab:8080]
     |
     |  one response back to RangeBox
     v
[RangeBox terminal shows the output]
```

**What the diagram shows, in words:**

1. The **student device** is the computer in front of you. It runs the browser.
2. The **browser** opens the OpenCyberRange page. The page is a website provided
   by the platform.
3. The **OpenCyberRange page** launches the exercise and shows the RangeBox
   desktop inside the browser.
4. **RangeBox** is the remote Linux desktop. It is your practice workstation.
   It is not the same computer as your student device.
5. The **RangeBox terminal** sends one request to the **assigned target**,
   `rangebox.lab:8080`.
6. The target sends one **response** back to RangeBox. The terminal displays it.
7. The **public internet** is not part of this path. Do not use it in this
   activity.

## The Trust Boundary

A **trust boundary** is the line between what you are allowed to use and what
you are not. In this chapter, the boundary is simple: the only network system you
may contact is the assigned target.

| System | Is it the target? | May you contact it? |
|---|---|---|
| Student device | No. It is your local computer. | You use it only to view the platform. |
| OpenCyberRange page | No. It is the platform that launches the exercise. | Yes, through your browser. |
| RangeBox desktop | No. It is your remote practice workstation. | Yes, it is provided for the activity. |
| Assigned target `rangebox.lab:8080` | **Yes.** | **Yes. This is the only network target in scope.** |
| Public internet | No. | **No.** Do not browse real websites from RangeBox. |
| School network or another student's lab | No. | **No.** Do not test or scan it. |

The `.lab` ending is a practice name. `rangebox.lab` is not a public website.

## How a Request Travels

Use this school-friendly example:

- The **IP address** is like the school's street address.
- The **port** is like the office number inside the school.
- The **service** is the person or office that handles your request.
- The **request** is the note you send: "Please give me the welcome file."
- The **response** is the note that comes back with the file or an error.

In order:

1. The **client** decides what it wants.
2. **DNS** turns the **hostname** into an **IP address**.
3. The request goes to that IP address and to a **port**.
4. The **service** listening on that port handles the request.
5. The server sends a **response** back to the client.

## Ports Are Numbers, Not Doors

A port is a number in the address. It is not a door, a hole, or a physical
socket. Nothing is physically opened when a service uses a port.

Think of a school building:

- The building has one street address. That is the **IP address**.
- The building has many office numbers. Those are **ports**.
- The office that answers is the **service**.
- A request goes to the building address **and** the office number.

A web developer sees the same idea on one computer:

| URL | Host | Port | What it usually means |
|---|---|---|---|
| `http://localhost:3000` | `localhost` | `3000` | A local test server, often a development tool. |
| `http://localhost:8080` | `localhost` | `8080` | Another local service, often an alternate web port. |
| `http://rangebox.lab:8080` | `rangebox.lab` | `8080` | The practice target for this activity. |

Common web ports:

| Port | Usual service |
|---|---|
| `80` | HTTP, ordinary web pages |
| `443` | HTTPS, protected web pages |
| `8080` | An alternate HTTP port, often used by practice servers and development tools |

A port number does not tell you whether a service is safe, new, or important. It
only tells the network which service should receive the request. In this
activity, use only port `8080` on `rangebox.lab`. Do not try other ports.

## Reading a URL

```text
http://rangebox.lab:8080/welcome.txt
│      │             │    │
│      │             │    └─ path: the file you are asking for
│      │             └────── port: which service should answer
│      └──────────────────── hostname: the name of the target
└─────────────────────────── protocol: the rules for the request
```

| Part | Value in this activity | What it means |
|---|---|---|
| Protocol | `http` | Use the HTTP rules for the request. |
| Hostname | `rangebox.lab` | The name of the assigned target. |
| Port | `8080` | The service that should receive the request. |
| Path | `/welcome.txt` | The file you are asking for. |

## Walkthrough: One Read-Only Request

You will run one command. It asks the target for a text file. It does not change
anything on the target.

### Step 1: Confirm the target and the scope

**Current directory:** any folder inside RangeBox is fine for this activity.

Check the exercise page. Confirm that the target is:

```text
rangebox.lab:8080
```

If your exercise shows a different target, stop and ask your teacher for the
exact URL. Use only the target and URL shown in that exercise; do not guess. Do
not use a public website.

### Step 2: Run the request

In the RangeBox terminal, run:

```bash
curl -v http://rangebox.lab:8080/welcome.txt
```

**You should see:** connection details, the request, the response, and the body
of the welcome file.

The option `-v` means **verbose**: show the connection details as well as the
file. The command is read-only. It asks for a file; it does not upload or change
anything.

If you prefer a template:

```text
curl -v http://TARGET:PORT/PATH
```

Replace `TARGET`, `PORT`, and `PATH` only with values from your exercise. Do not
guess a different target, port, or path.

### Step 3: Read the connection lines

Lines that start with `*` are connection details from `curl`. They are not part
of the server's response.

**You may see** lines like:

```text
* Trying <lab IP address>:8080...
* Connected to rangebox.lab (<lab IP address>) port 8080
```

**What to notice:**

- `rangebox.lab` is the **hostname**.
- The address in angle brackets is the **IP address** that DNS returned. It may
  be different each time the lab starts.
- `8080` is the **port**.
- The exact IP address belongs to your exercise. Do not copy an address from
  this page or share real network addresses.

If you see `Could not resolve host`, DNS could not turn the hostname into an IP
address. Check that you are in the correct exercise and that the target is
`rangebox.lab`. Ask your teacher if it still fails.

### Step 4: Read the request lines

Lines that start with `>` are the **request** that `curl` sent to the server.

**You may see** lines like:

```text
> GET /welcome.txt HTTP/1.1
> Host: rangebox.lab:8080
> User-Agent: curl/...
> Accept: */*
>
```

**What to notice:**

- `GET` means "please send me this file". It is a read-only request method.
- `/welcome.txt` is the **path**.
- `HTTP/1.1` is the **protocol** version.
- `Host: rangebox.lab:8080` repeats the hostname and port.
- The blank `>` line marks the end of the request headers.

### Step 5: Read the response lines

Lines that start with `<` are the **response** from the server.

**You may see** lines like:

```text
< HTTP/1.1 200 OK
< Content-Type: text/plain
< Content-Length: ...
<
```

**What to notice:**

- `HTTP/1.1` is the protocol version.
- `200 OK` is a status code that means the request succeeded.
- `Content-Type: text/plain` says the body is plain text.
- `Content-Length` says how many bytes are in the body.
- Header order and extra headers may differ. That is normal.

| Status code | Plain meaning |
|---|---|
| `200` | Success. The server sent what you asked for. |
| `301` or `302` | The file moved to another address. |
| `403` | The server refused the request. |
| `404` | The server could not find that path. |
| `500` | The server had an internal problem. |

### Step 6: Read the body

After the response headers, `curl` prints the **body** of the file. This is the
same welcome text you saw in the first activity. It may include the training
token. You do not need to submit it again; this activity has **no flag**.

### Step 7: Stop at the end of the response

When the body ends and the prompt returns, the request is finished. Do not run
the command against another host or port.

## Matching Check

Match each term in the left column with one definition in the right column.
Write the letter next to the number. Cover the answer key before you start.

| # | Term | Letter | Definition |
|---|---|---|---|
| 1 | Network | | A. A number-based address of a host on a network. |
| 2 | Host | | B. A device or program that asks for data or a service. |
| 3 | Client | | C. The message a server sends back. |
| 4 | Server | | D. Two or more devices that can send data to each other. |
| 5 | IP address | | E. A number that identifies which service on a host should receive a request. |
| 6 | Hostname | | F. A human-readable name that maps to an IP address. |
| 7 | Protocol | | G. A device or program that provides data or a service. |
| 8 | Service | | H. An agreed set of rules for communication. |
| 9 | Port | | I. A program on a server that provides something, such as a web page. |
| 10 | Request | | J. Any device on a network with an address. |
| 11 | Response | | K. The message a client sends to ask for something. |

**Answer key:** 1-D, 2-J, 3-B, 4-G, 5-A, 6-F, 7-H, 8-I, 9-E, 10-K, 11-C.

If you missed a term, reread its row in **Words to Know** and say the definition
in your own words.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong exercise or target | `Could not resolve host` | Check that your exercise includes `rangebox.lab:8080`. Ask your teacher. Do not try a public website. |
| Lab is not ready | `Connection refused` or `Failed to connect` | Wait a moment, then try once more. If it still fails, stop and relaunch the exercise. Do not try other ports. |
| Path is wrong | `404 Not Found` | Check the spelling and case of `/welcome.txt`. Linux paths are case-sensitive. |
| Server refuses the request | `403 Forbidden` | Stop. Do not try to bypass it. Ask your teacher. |
| Server problem | `500 Internal Server Error` | Stop. Relaunch the exercise or ask your teacher. |
| No response | The command seems to hang | Wait a short time. If it still does not return, press `Ctrl` + `C` to cancel, then ask your teacher. |
| You see a real website | A search page or shopping site | Stop. You are outside the lab. Close that page and return to the exercise. |
| You are not sure which system you are on | You see your own device's desktop | You are not in RangeBox. Return to the OpenCyberRange page and open RangeBox. |

## Record Your Evidence

Copy this table into your notes and fill it in.

| Question | Your answer |
|---|---|
| What is the hostname in the URL? | |
| What is the port? | |
| What is the path? | |
| What is the IP address that DNS returned? | |
| Which status code did the server return? | |
| What did the body contain? | |

Then answer these questions.

1. Which system is your student device?
2. Which system is RangeBox?
3. Which system is the assigned target?
4. Why is the public internet out of scope?
5. What is the difference between a hostname and an IP address?
6. What does DNS do?
7. Why is a port not a physical opening?
8. Which lines in `curl -v` show the request?
9. Which lines show the response?
10. What would you do if you saw `Could not resolve host`?

## What Success Looks Like

You are ready to continue when you can show:

- the `curl -v` command and its output;
- the hostname, port, path, IP address, and status code you observed;
- a clear explanation of client, server, request, and response;
- a clear statement that the only network target was `rangebox.lab:8080`;
- a clear statement that the public internet was not used;
- one recovery step for a name-resolution or connection failure.

This activity has **no flag**. Your evidence is your notes and your explanation.

## Key Takeaways

- A network is two or more devices that can send data to each other. A host is
  any device on that network with an address.
- A client asks; a server responds. A host can act as either one.
- A hostname is a name; an IP address is a number. DNS maps the name to the
  number.
- A protocol is a set of rules. HTTP is the ordinary web protocol; HTTPS is the
  protected version.
- A service is a program that provides something. A port is the number that
  tells the network which service should receive the request.
- A port is not a door or a hole. It is a number in the address.
- Your student device, the OpenCyberRange page, RangeBox, the assigned target,
  and the public internet are different places.
- Only the assigned target is in scope. Do not scan, probe, or browse the public
  internet from the lab.

When you are ready, continue with [RangeBox File Hunt](02_File_Hunt.md).
