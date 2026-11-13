# Exercise 12.2: Two-Router Transit

## Goal

Prove that a workstation reaches a service through two routers, and explain the
return route that makes the reply possible.

## Topology

```text
h1 ---- r1 ==== r2 ---- svc
     link     transit   link
```

Each `----` or `====` is a separate `/29`. The engine allocates them at spawn
time; use the status endpoints, not fixed addresses.

## Step 1: Read both routers

```bash
curl -s http://<r1-management-ip>:8080/status
curl -s http://<r2-management-ip>:8080/status
```

Record:

- r1's workstation link and transit link;
- r2's transit link and service link;
- the peer address of `svc` on r2.

## Step 2: Read the routing tables

```bash
ssh analyst@<r1-management-ip>
ip route

ssh analyst@<r2-management-ip>
ip route
```

Expected:

- r1 has a route to the service link through r2;
- r2 has a route to the workstation link through r1;
- both routers have `ip_forward=1`.

A forward route without a return route produces a request that leaves but never
gets a reply. That is the failure this lab teaches you to spot.

## Step 3: Follow the path

From h1, use the service **link** address from r2's status document:

```bash
curl -s http://<svc-link-address>/flag
```

Expected: `OCR{tw0_r0ut3rs_0n3_p4th}`.

## Analysis

1. Why does h1 need only a default route?
2. What breaks if r2 has no route to the workstation link?
3. Which router is the better place to inspect traffic between the links?
4. How would you document the two transit paths for an on-call engineer?

## Defensive takeaway

Transit links are inspection points. Document both directions of every static
route, monitor forwarding, and test the return path — not only the request.
