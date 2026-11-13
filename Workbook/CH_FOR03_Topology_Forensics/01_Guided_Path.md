# Exercise 2.2: Guided Path Reconstruction

## Goal

Follow a workstation-to-service request through one router and recover the case
token, recording the evidence at each hop.

## Step 1: Identify the devices

```bash
curl -s http://<router-management-ip>:8080/status
```

The status document lists:

- `node` and `role`;
- each `peer`, its `ip`, `peer_ip`, and `/29` `subnet`;
- the default `gateway` for a host or service.

Record the router's link to the workstation and its link to `case-svc`.

## Step 2: Read the workstation route

```bash
ssh analyst@<workstation-management-ip>
ip route
```

Expected: a `default via <router-link-address>` route and the connected
workstation `/29`. The workstation does not need a route to the service subnet.

## Step 3: Confirm forwarding

```bash
ssh analyst@<router-management-ip>
cat /proc/sys/net/ipv4/ip_forward
ip route
```

Expected: `1`, plus a connected route for each link.

## Step 4: Follow the path

From the workstation, use the case service's **link** address from the router
status:

```bash
wget -qO- http://<case-svc-link-address>/flag
```

Expected: `OCR{f0r3ns1c_p4th_gu1d3d}`.

## Step 5: Record the path

Complete this record:

| Hop | Device | Interface / link | Peer | Subnet | Evidence |
|---|---|---|---|---|---|
| 1 | workstation | | router | | default route |
| 2 | router | | case-svc | | connected route, forwarding |
| 3 | case-svc | | router | | token response |

## Analysis

1. Why is the link address better evidence than the management address?
2. What would a missing return route look like from the workstation?
3. Which single command proves the router forwarded rather than dropped traffic?
4. Why should the path record not include the token itself?

## Defensive takeaway

A path record should name each hop, interface, peer, and subnet. That is what
lets another analyst reproduce the finding.
