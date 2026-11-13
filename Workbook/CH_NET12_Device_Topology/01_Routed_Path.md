# Exercise 12.1: Follow the Routed Path

## Goal

Prove that the workstation reaches the protected service through the router,
not through a direct link.

## Step 1: Read the topology

From the tester or your workstation, query each node:

```bash
curl -s http://<r1-management-ip>:8080/status
curl -s http://<h1-management-ip>:8080/status
curl -s http://<svc-management-ip>:8080/status
```

The status document reports:

- `role`: `router`, `host`, or `service`;
- `links`: each peer, the local link address, and the peer address;
- `gateway`: the host or service default next hop.

Record the router's two link addresses. They are on different `/29` subnets.

## Step 2: Confirm the host default route

```bash
ssh analyst@<h1-management-ip>
ip route
```

Expected: a `default via <r1-link-address>` route, plus the connected `/29` for
the host link.

The host does not have a route to the service subnet. It sends that traffic to
the default gateway.

## Step 3: Confirm forwarding on the router

```bash
ssh analyst@<r1-management-ip>
cat /proc/sys/net/ipv4/ip_forward
ip route
```

Expected: `1`, and a connected route for each link. The router knows both
subnets because both interfaces are attached.

## Step 4: Reach the service through the router

From `h1`, use the service's **link address** from the router status document,
not its management address:

```bash
curl -s http://<svc-link-address>/flag
```

Expected: `OCR{t0p0l0gy_r0ut3d}`.

If you use the management address, you are testing the management plane, not the
routed path. The link address proves the packet left `h1`, crossed `r1`, and
arrived on the service link.

## Analysis

1. Why does `h1` not need a route to the service subnet?
2. What would happen if `r1` had forwarding disabled?
3. Which device is the natural place to filter or log this traffic?
4. Why is a per-session `/29` safer than a fixed lab subnet?

## Defensive takeaway

A routed segment is a control point. Default routes, forwarding, and firewall
policy on that router decide whether a compromised host can reach a protected
service, and the router is where you can observe the attempt.
