# Exercise 2.1: Network Communication and Ports

This activity explains how a client and server communicate. You will read a
labelled connection example, make one safe request to the **RangeBox Network
Basics** lab, and interpret the connection state without treating it as a
vulnerability.

## Before You Begin

### Where to run this activity

| Place | What it is | Used here? |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Only for reading and notes. |
| **RangeBox desktop** | The remote Linux desktop. | Yes. |
| **RangeBox terminal** | The text window inside RangeBox. | **Yes. Run every command here.** |
| **Assigned target** | `network.lab:8080` for the Network Basics lab. | **Yes. This is the only target in scope.** |

Open the **RangeBox Network Basics** exercise. The target is `network.lab` on
port `8080`. If the exercise panel shows a different hostname or port, stop and
ask. Do not try other ports.

### What you need

- [ ] The Network Basics lab running.
- [ ] The RangeBox terminal open.
- [ ] A notes file for the connection table.
- [ ] About **25–30 minutes**.

### What you will be able to do

By the end of this activity, you will be able to:

- explain IP address, hostname, protocol, TCP, UDP, service, port, request,
  response, and connection state;
- identify the source, destination, local port, remote port, and direction in a
  connection;
- tell listening, established, closed, filtered, and unreachable apart;
- explain why an open port is not automatically a vulnerability;
- record connection evidence with a confidence level.

## Words to Know

| Term | What it means |
|---|---|
| **IP address** | A number-based address of a host. |
| **Hostname** | A name that maps to an IP address, such as `network.lab`. |
| **Protocol** | Agreed rules for communication. HTTP is the web protocol. |
| **TCP** | A connection-oriented protocol. It sets up a connection, tracks it, and closes it. HTTP uses TCP. |
| **UDP** | A connectionless protocol. It sends messages without setting up a TCP-style connection. |
| **Service** | A program that provides something, such as a web page. |
| **Port** | A number that identifies a service on a host. |
| **Request** | A message a client sends to a server. |
| **Response** | A message a server sends back. |
| **Local port** | The port on the client side of a connection. It is often chosen automatically. |
| **Remote port** | The port on the server side. For this lab it is `8080`. |
| **Connection state** | What the network stack reports about a socket, such as `LISTEN`, `ESTABLISHED`, `CLOSED`, or `FILTERED`. |

## A Labelled Client-Server Example

This is a synthetic example, not a real capture. It uses placeholders so no lab
address is invented.

```text
CLIENT (RangeBox)                         SERVER (assigned target)
IP: CLIENT_IP                             IP: TARGET_IP
local port: CLIENT_PORT                   remote port: 8080
        |                                         |
        |  request: GET /status.json HTTP/1.1     |
        |---------------------------------------->|
        |                                         |
        |  response: HTTP/1.1 200 OK              |
        |<----------------------------------------|
        |                                         |
```

Read it in this order:

1. **Source:** the client, `CLIENT_IP:CLIENT_PORT`.
2. **Destination:** the server, `TARGET_IP:8080`.
3. **Direction:** client to server for the request; server to client for the
   response.
4. **Protocol:** HTTP inside TCP.
5. **Local port:** the client's port.
6. **Remote port:** the server's port, `8080`.

The server is **listening** on port `8080`. The client makes an **outbound
connection** from a local port. The connection becomes **established** while the
request and response are in progress.

## Connection States

| State | Plain meaning | What it does not prove |
|---|---|---|
| **LISTEN** | A service is waiting for connections on a port. | That the service is vulnerable, or that you may connect. |
| **ESTABLISHED** | A connection is active. | That the traffic is safe or malicious. |
| **CLOSED** | No connection is open on that port. | That the host is down or the service never existed. |
| **FILTERED** | No response arrived; something may be blocking it. | That a firewall is present, or that the port is closed. |
| **UNREACHABLE** | The host or network could not be reached. | That the target is vulnerable or safe. |

An **open port is not a vulnerability**. It only means a service accepts
connections. A vulnerability depends on the software, version, configuration,
and behaviour. This activity does not test for vulnerabilities.

## Walkthrough

### Step 1: Confirm the target

Open the exercise panel. Confirm:

```text
hostname: network.lab
port: 8080
path: /status.json
```

**Why:** a request to the wrong host or port is outside scope.

**If the exercise panel differs:** stop and ask. Do not try another target.

### Step 2: Make one request

In the RangeBox terminal:

```bash
curl -v http://network.lab:8080/status.json
```

**Why:** `-v` shows the connection details, the request, and the response.

**Expected result:** connection lines, request lines, response headers, and a
JSON body. The `X-OCR-Token` header contains the lab flag.

**What to notice:**

- `* Trying ...:8080` shows the remote port.
- `* Connected to network.lab ... port 8080` confirms the destination.
- Lines starting with `>` are the request.
- Lines starting with `<` are the response.
- `HTTP/1.1 200 OK` is the status.

If you have not submitted the flag for the Network Basics lab, copy the
`X-OCR-Token` value into the exercise panel. This page preserves that lab flag.

### Step 3: Identify the endpoints

Write down:

| Field | Your answer |
|---|---|
| Client host | RangeBox |
| Client IP | the address shown in the `Trying` line |
| Server hostname | `network.lab` |
| Server port | `8080` |
| Protocol | HTTP over TCP |
| Direction of request | client to server |
| Direction of response | server to client |

**Uncertainty:** the client IP and remote IP may be private lab addresses. Do
not copy them into public notes or share them outside class.

### Step 4: Look for a listener

```bash
ss -tuln
```

**Why:** this shows listening sockets inside RangeBox. It may not show the
target's listener, because the target is a separate container.

**Expected result:** zero or more listeners. If `:8080` is not shown, that is
normal. The target's port is on the target, not inside RangeBox.

**If `ss` is not found:** try `netstat -tuln`. If neither works, ask your
teacher. Do not install a tool.

### Step 5: Interpret a synthetic connection

Read this synthetic line:

```text
CLIENT_IP:51544 -> TARGET_IP:8080  TCP  ESTABLISHED
```

Answer:

1. Which side is the client?
2. Which side is the server?
3. Which is the local port?
4. Which is the remote port?
5. What is the direction?
6. What does `ESTABLISHED` mean?
7. Does this prove a vulnerability? Why not?

A strong answer identifies the client as the source, the server as the
destination, `51544` as the local port, `8080` as the remote port, and says that
an established connection only means communication is active.

### Step 6: Compare states

Read each synthetic line:

```text
TARGET_IP:8080  TCP  LISTEN
CLIENT_IP:51544 -> TARGET_IP:8080  TCP  ESTABLISHED
CLIENT_IP:51545 -> TARGET_IP:8080  TCP  CLOSED
CLIENT_IP:51546 -> TARGET_IP:9999  TCP  FILTERED
```

Write one sentence for each state. Then answer:

- Which line shows a service waiting?
- Which line shows an active connection?
- Which line shows no open connection?
- Which line shows no response?
- Which line tells you the least about the service?

**Important:** `FILTERED` and `UNREACHABLE` are observations, not proof of an
attack or a vulnerability.

## If You Get Stuck

| Problem | What you may see | Safe next step |
|---|---|---|
| Wrong target | The exercise panel differs from the workbook | Stop and ask. Do not try another host or port. |
| Name resolution failure | `Could not resolve host` | Check the spelling and the exercise. Ask your teacher. |
| Connection refused | `Connection refused` | Check that the lab is running and the port is `8080`. |
| Timeout | No response | Wait 10 seconds, press `Ctrl` + `C`, check the lab status. |
| No listener in `ss` | `ss` shows nothing on 8080 | That is normal; the target is a separate container. |
| `ss` missing | `command not found` | Try `netstat -tuln`; otherwise ask. Do not install tools. |
| Unsure about a state | A line says `FILTERED` or `UNREACHABLE` | Record the observation and your uncertainty. Do not guess. |

## Record Your Evidence

| Field | Value |
|---|---|
| Target hostname | |
| Target port | |
| Request path | |
| Status code | |
| Protocol | |
| Connection state observed | |
| Listener visible in RangeBox? | |
| What I can conclude | |
| What I cannot conclude | |
| Confidence | Low / Medium / High |

## What Success Looks Like

You are ready to continue when you can show:

- one request to the assigned target;
- the source, destination, local port, remote port, and direction explained;
- the request and response identified in `curl -v`;
- listening, established, closed, filtered, and unreachable explained;
- one sentence saying that an open port is not a vulnerability;
- one uncertainty statement about what the evidence does not prove.

This activity uses the **Network Basics** lab flag. If you have not submitted it,
copy the `X-OCR-Token` value into the exercise panel.

## Key Takeaways

- A hostname maps to an IP address; a port identifies a service.
- A client uses a local port to reach a remote port.
- TCP sets up a connection; UDP does not.
- `LISTEN` means waiting; `ESTABLISHED` means active; `CLOSED`, `FILTERED`, and
  `UNREACHABLE` describe different observations.
- An open port is not automatically a vulnerability.
- Only the assigned target and port are in scope.

Next: [Introductory Service Enumeration](06_Introductory_Service_Enumeration.md).
