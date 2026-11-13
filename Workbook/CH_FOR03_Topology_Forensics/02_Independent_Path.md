# Exercise 2.3: Independent Path Reconstruction

## Goal

Reconstruct the routed path without step-by-step instructions, identify the case
service among a decoy, and produce a reproducible evidence record.

## What you know

- A workstation contacted two services through one router.
- One service is the protected case service; the other is a decoy.
- The router status endpoint reports its role and links.
- The node status endpoint is available on each management address.

## What to produce

1. A list of every node and its role.
2. The router's links, peer addresses, and `/29` subnets.
3. The workstation default route.
4. Proof of IPv4 forwarding.
5. The case service link address and the token.
6. A one-paragraph path record another analyst can follow.

## Evidence record template

| Item | Value |
|---|---|
| Workstation management IP | |
| Router management IP | |
| Case service management IP | |
| Decoy management IP | |
| Workstation default next hop | |
| Router forwarding value | |
| Case service link subnet | |
| Decoy link subnet | |
| Token (do not share) | |

## Rules

- Do not change routes or forwarding.
- Verify the service identity before treating it as evidence.
- Use the link address for the final request.
- Keep the record factual: node, interface, peer, subnet, result.

## Analysis

1. How did you distinguish the case service from the decoy?
2. Which evidence proves the request crossed the router?
3. What would you record if the token request failed?
4. Why does an independent reconstruction need a repeatable record?

## Defensive takeaway

Independent reconstruction is the test of a forensic method. Verify the service,
record the path, and make the result reproducible.
