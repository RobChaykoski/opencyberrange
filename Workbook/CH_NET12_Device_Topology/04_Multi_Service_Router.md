# Exercise 12.4: Multi-Service Router

## Goal

Map a router with three links, record the topology, and reach two services
through it.

## Step 1: Map the router

```bash
curl -s http://<r1-management-ip>:8080/status
```

Expected: three links — workstation, `svc1`, and `svc2`. Record each peer, local
address, peer address, and `/29` subnet.

## Step 2: Read the host route

```bash
ssh analyst@<h1-management-ip>
ip route
```

Expected: one default route via r1 and the connected workstation link. The host
does not need routes to the service links because r1 is connected to both.

## Step 3: Reach both services

Use the service link addresses from r1's status document:

```bash
curl -s http://<svc1-link-address>/flag
curl -s http://<svc2-link-address>:8080/status
```

Expected: the flag from `svc1` and a status document from `svc2` with
`"node": "svc2"`.

## Step 4: Write the topology record

Complete this table for the current session:

| Node | Role | Management IP | Link peers | Link subnets |
|---|---|---|---|---|
| h1 | host | | | |
| r1 | router | | | |
| svc1 | service | | | |
| svc2 | service | | | |

A useful record names the link, both endpoints, and the subnet. Do not record the
flag.

## Analysis

1. Why can one router serve two services without extra host routes?
2. What would change if the services were on the same link?
3. Which link would you monitor to detect scanning of both services?
4. Why is the management address a poor proof of the data path?

## Defensive takeaway

Multi-service routers concentrate reachability. Document every link and service,
then monitor the paths you intend to expose and remove the ones you do not.
