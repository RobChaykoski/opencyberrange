# Exercise 12.5: Network Appliance Segmentation

## Goal

Map a dual-homed OpenWrt appliance, prove that a protected service on an
internal segment is not directly reachable, and pivot through the appliance to
retrieve the flag.

## Before You Begin

- Launch the exercise and connect with RangeBox or the VPN.
- The appliance management address is shown in the exercise panel.
- Sign in to the appliance with the credentials shown in the exercise.

The appliance has two interfaces:

| Interface | Network | Reachable from your workstation |
|---|---|---|
| training interface | training network | yes |
| control interface | protected control segment | no |

Interface names depend on start order; use `ip -4 addr show` and the
address ranges rather than assuming `eth0` or `eth1`. The protected service has
no address on the training network. The appliance is the only device attached
to both segments.

## Step 1: Map the appliance

```bash
ssh root@<appliance-address>
ip -4 addr show
ip route
```

Identify the training-network address and the control-segment address. Notice
that the appliance has a connected route to each segment.

## Step 2: Confirm the segmentation

From your workstation, try to reach the protected service directly:

```bash
curl -s --connect-timeout 3 http://protected/flag
```

The name does not resolve on the training network, and there is no route to the
control segment. This is the segmentation working as designed.

From the appliance, confirm the protected service is alive:

```bash
nslookup protected
wget -q -O - http://protected/flag
```

## Step 3: Inspect the forward policy

```bash
nft list chain inet labfw forward
```

The forward chain is default-deny. Only established and related traffic is
accepted. That policy applies to packets the appliance **forwards** between the
two interfaces. Traffic addressed to the appliance, such as your SSH session,
is handled by the input path, so a shell on the appliance can reach both
segments even while forwarding is denied.

## Step 4: Pivot with an SSH local forward

An SSH local forward terminates the connection at the appliance and opens a new
connection from there. That makes it a simple pivot through a segmented host.

On your workstation, resolve the protected address first. You can read it from
the appliance:

```bash
ssh root@<appliance-address> "nslookup protected"
```

Then open the tunnel (replace `<protected-ip>` with the resolved address):

```bash
ssh -N -L 18080:<protected-ip>:80 root@<appliance-address>
```

In a second terminal:

```bash
curl -s --noproxy '*' http://127.0.0.1:18080/flag
```

The flag is returned through the tunnel. You never joined the control segment.

## Step 5: Clean up

Close the tunnel with `Ctrl+C` or kill the background SSH process. Do not leave
forwards running when you finish the exercise.

## What Just Happened?

The protected service was never routable from your workstation. The appliance
was reachable because it has an interface on the training network, and it could
reach the protected service because it also has an interface on the control
segment. SSH local forwarding let the appliance relay one TCP connection on your
behalf.

This is a common real-world path: a jump host or management appliance bridges
segments, and the firewall policy protects routed traffic but not the shell on
the appliance itself.

## Analysis Questions

1. Why does the protected service have no route from the workstation?
2. What is the difference between the `input`, `forward`, and `output` chains in
   this lab?
3. Why does the default-deny forward policy not block the SSH local forward?
4. What logging would show that a learner pivoted through the appliance?
5. How would you separate management access from the data path on a production
   appliance?

## Defensive Takeaways

- Treat a dual-homed appliance as both a control and a pivot point.
- Restrict who can sign in to the appliance, and log SSH local forwards.
- Default-deny forwarding is necessary but not sufficient: a shell on the
  appliance can still reach both segments.
- Keep management access on a separate path from learner traffic.
- Review appliance firewall rules after every change and test both the allowed
  and denied paths.

## If You Get Stuck

- If SSH is refused, the appliance may still be starting. Wait a few seconds and
  retry.
- If the tunnel returns connection refused, re-resolve the protected address on
  the appliance and make sure the tunnel uses the control-segment address.
- If `curl` uses a proxy, pass `--noproxy '*'` as shown.
