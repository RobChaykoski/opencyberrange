# Exercise 2.6: Detecting a WebSocket C2 Tunnel

## Before You Begin

Exercise 2.6 moves from reading a capture to proving that a session is
command-and-control when the payload never appears as plain HTTP.

Make sure you have:

- [ ] Launched the exercise and opened the RangeBox desktop
- [ ] A terminal open inside the desktop
- [ ] The **WebSocket Relay** and **Network Tap** addresses from the panel
- [ ] `nc`, `tcpdump`, `tshark`, and Wireshark available
- [ ] The beacon interval from the earlier traffic-analysis labs

---

## Scenario

Northwind Freight rebuilt a dispatch workstation after a ransomware scare.
The rebuild restored an application profile that still points at a "sync
service", and the workstation is beaconing again.

The difference this time is the transport. The implant does not talk to the
internet directly. It opens a WebSocket to a public relay that looks like an
ordinary application endpoint, and the relay forwards the session to the real
tasking server on a protected segment. The tasking server has no route from the
lab network, so the relay is the only visible half of the conversation.

You are the SOC analyst on shift. Capture the segment from the network tap,
prove the WebSocket session is carrying command-and-control, and recover the
task key the real server returns.

---

## Your Objectives

- Explain why an attacker wraps C2 traffic in a WebSocket upgrade
- Capture lab traffic from the network tap and isolate the tunnel session
- Recognise the HTTP upgrade and the binary frames that carry the beacon
- Recover the task key from the tunneled payload
- Write a detection that flags the upgrade path rather than the payload

---

## Background: Why a WebSocket Tunnel

Most networks allow HTTP and HTTPS because the business runs on them. A
WebSocket starts life as an ordinary HTTP request with an `Upgrade` header and
then becomes a long-lived, bidirectional stream. To a proxy or a firewall it
looks like a modern application: a `GET` to a path, a normal user agent, and a
connection that stays open.

`wstunnel` turns that into a general-purpose tunnel. The client listens on a
local port and forwards every connection through the WebSocket to the server,
which opens the real connection to the destination. The bytes inside the tunnel
are not encrypted by `wstunnel`; TLS is the caller's job. That is what makes
this lab solvable: the tasking response travels as WebSocket binary frames in
cleartext.

The lab splits the conversation on purpose:

- the **relay** is on the lab network and is the only host the workstation can
  reach;
- the **tasking server** sits on an internal network with no address on the lab
  bridge, so the relay is the only route to it.

The network tap mirrors the lab bridge. You see the WebSocket session, not the
plain HTTP between the relay and the tasking server. Proving the tunnel is C2
therefore depends on the shape of the session, not on reading a clean request.

---

## Walkthrough

### Stage 1: Confirm the Relay

Start with the visible half of the conversation. A WebSocket-only listener
rejects a plain request, which is itself a useful fingerprint.

!!! target "Probe the relay with plain HTTP"
    Run this in the RangeBox terminal. The relay address is shown in the panel.

    ```bash
    curl -i http://c2-relay:8080/
    ```

    The answer is `400 Bad Request`. The listener is waiting for an `Upgrade:
    websocket` handshake and will not serve ordinary pages. That is normal for
    a relay, and it is exactly the behaviour an implant hides behind.

---

**Record Your Findings**

- What status code does the relay return to a plain `GET`?
- What does that tell you about the service?
- Is the relay a normal web application?

---

### Stage 2: Capture the Segment

The beacon checks in every few seconds, so a short capture is enough. Connect
to the tap and write the stream to a file.

!!! target "Capture one beacon cycle"
    Run this in the RangeBox terminal. The tap streams a live PCAP on TCP 9999.

    ```bash
    timeout 30 nc network-tap 9999 > /tmp/tunnel.pcap
    ls -l /tmp/tunnel.pcap
    ```

    The file should be a few kilobytes. If it is empty, the tap had not attached
    yet; wait a moment and capture again.

Start with a protocol overview so you know what you are looking at.

!!! target "Summarise the capture"
    Run this in the RangeBox terminal.

    ```bash
    tshark -r /tmp/tunnel.pcap -q -z io,phs
    ```

    You should see TCP and HTTP, with no DNS lookup for the tasking server. The
    workstation only knows the relay.

---

**Record Your Findings**

- Which two hosts appear in the capture?
- Which ports are in use?
- Is there a DNS lookup for the tasking server?

---

### Stage 3: Find the Upgrade

The handshake is the only part of the session an HTTP dissector can read. Pull
the requests and look at the path and headers.

!!! target "List the HTTP requests"
    Run this in the RangeBox terminal.

    ```bash
    tshark -r /tmp/tunnel.pcap -Y 'http.request' \
      -T fields -e frame.time_relative -e ip.src -e ip.dst \
      -e http.request.method -e http.request.uri -e http.user_agent
    ```

    The workstation sends a `GET /v1` to the relay with a browser user agent.
    `/v1` is the default `wstunnel` upgrade path prefix. A browser user agent
    on a path that serves no pages is the first anomaly.

Read the handshake in full to see the upgrade.

!!! target "Show the upgrade headers"
    Run this in the RangeBox terminal.

    ```bash
    tshark -r /tmp/tunnel.pcap -Y 'http.request' -V | grep -iE 'upgrade|connection|sec-websocket'
    ```

    `Connection: Upgrade`, `Upgrade: websocket`, and a `Sec-WebSocket-Key`
    confirm the session becomes a bidirectional stream. After this exchange the
    HTTP dissector shows nothing else: the beacon travels in WebSocket frames.

---

**Record Your Findings**

- What path does the client request?
- What user agent does it present?
- Which header turns the request into a tunnel?
- Why does `tshark -Y http.request` show only one request?

---

### Stage 4: Recover the Task Key

`wstunnel` does not encrypt the tunneled bytes. The tasking response is inside
WebSocket binary frames, so a byte search over the capture finds it.

!!! target "Search the capture for the task key"
    Run this in the RangeBox terminal.

    ```bash
    strings /tmp/tunnel.pcap | grep -o 'OCR{[^}]*}'
    ```

    The marker is the `task_key` field the tasking server returned. In
    Wireshark, follow the TCP stream to the relay and look for the JSON body
    inside the frame payload.

    If `strings` is not installed, the same search works in Python:

    ```bash
    python3 -c "d=open('/tmp/tunnel.pcap','rb').read(); i=d.find(b'OCR{'); print(d[i:d.find(b'}',i)+1].decode())"
    ```

---

**Record Your Findings**

- What is the task key?
- Which side of the tunnel sent it?
- Why is the response visible even though the session is a WebSocket?

---

### Stage 5: Write the Detection

A detection that matches the payload only works until the attacker changes it.
Match the behaviour instead: a WebSocket upgrade to a path the application does
not use, held open for a long time.

!!! target "Draft a Suricata rule"
    Save this as `ws-c2.rules`. It alerts on a `GET` upgrade to `/v1` with a
    browser user agent, which is the shape this lab produces.

    ```text
    alert http any any -> any any (msg:"OCR WebSocket upgrade to non-application path"; \
      flow:established,to_server; http.method; content:"GET"; \
      http.uri; content:"/v1"; http.header; content:"Upgrade|3a| websocket"; \
      classtype:trojan-activity; sid:9000001; rev:1;)
    ```

    Test it against the capture:

    ```bash
    suricata -r /tmp/tunnel.pcap -S ws-c2.rules -l /tmp/suri-out
    grep -h 'WebSocket' /tmp/suri-out/fast.log
    ```

    If `suricata` is not installed in your desktop, write the equivalent
    `tshark` display filter and explain in your notes why the header, not the
    payload, is the durable signal.

!!! target "Compare with the proxy log view"
    A proxy or Zeek sensor records the same handshake. In Zeek, `http.log`
    shows the upgrade request and newer versions add a `websocket.log` entry
    for the session. Either way, the detection question is the same: does this
    host normally open long-lived WebSocket sessions to this destination?

---

**Record Your Findings**

- What field makes the rule resilient to a payload change?
- What would you baseline to reduce false positives?
- Which other hosts in a real network would you check after this alert?

---

## Analysis Questions

**1. The relay is a legitimate-looking service and the tunnel is not encrypted by `wstunnel`. Why does the attacker still gain an advantage?**

??? note "Reveal Answer"

    The advantage is blending, not secrecy. The session starts as an allowed
    HTTP request and becomes a long-lived stream, so a firewall that permits
    HTTP and HTTPS has no reason to block it. The payload is visible to anyone
    who captures the stream, but most monitoring stops at the handshake and
    never reassembles WebSocket frames. The attacker trades confidentiality for
    the ability to cross the perimeter and to hide the real destination behind a
    relay.

**2. What makes a WebSocket upgrade suspicious in this capture, and what would make the same upgrade benign in a real network?**

??? note "Reveal Answer"

    Suspicious here: a workstation opens a long-lived upgrade to `/v1`, a path
    that serves no application, with a browser user agent, at a fixed interval,
    and never loads any other resource from that host. Benign: a known
    application such as a chat client or an interactive dashboard, to a path the
    asset owner documents, with a user agent and TLS certificate that match the
    vendor, and with normal user-driven traffic around it. The detection needs
    both the shape of the session and an asset-owner baseline.

**3. The tasking server has no route from the lab network. How does that change your incident response compared with a direct C2 connection?**

??? note "Reveal Answer"

    You cannot reach or scan the real server, so containment has to start at the
    relay: block the relay destination, then hunt for every host that opened the
    same upgrade. The relay is shared infrastructure, so its logs may show other
    victims; that makes it a threat-intelligence source as well as a block
    target. For the workstation, isolate it, collect memory and disk, and treat
    the task key as an indicator that the implant completed a check-in.

## Key Takeaways

- A WebSocket tunnel looks like an allowed HTTP request that never ends. The
  upgrade is the durable detection point, not the payload.
- `wstunnel` forwards bytes without encrypting them, so a full capture can still
  recover tasking when the HTTP dissector shows only the handshake.
- A relay hides the real destination. Containment starts with the relay and with
  every host that used it, not with a scan of the protected segment.
- Fixed-interval beaconing plus a browser user agent on a non-application path
  is a stronger signal than any single indicator.
- Writing the detection against the handshake keeps it useful after the attacker
  changes the payload or the encoding.
