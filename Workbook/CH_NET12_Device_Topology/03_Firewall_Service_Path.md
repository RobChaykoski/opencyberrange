# Exercise 12.3: Firewall the Service Path

## Goal

Apply an nftables forward policy on the router: keep the flag service on port 80
reachable and block the status port 8080.

## Step 1: Confirm the path before policy

From h1, use the service link address from the router status:

```bash
curl -s http://<fw-management-ip>:8080/status
curl -s http://<svc-link-address>/flag
curl -s http://<svc-link-address>:8080/status
```

Both should work before you add a rule. If they do not, fix reachability first.

## Step 2: Apply a forward-chain policy

The router keeps `no-new-privileges`, so there is no `sudo` here. `fwctl` is the
scoped helper on the node: it applies a ruleset file you own and prints the live
rules.

```bash
ssh analyst@<fw-management-ip>

cat > /srv/fw/policy.nft <<'NFT'
table inet ocr {
  chain forward {
    type filter hook forward priority 0; policy accept;
    tcp dport 8080 drop
  }
}
NFT

fwctl apply /srv/fw/policy.nft
fwctl show
```

`fwctl` only accepts `show` and `apply` for files under `/srv/fw`, and the
apply runs as root inside this router container. Nothing outside the node is
reachable through it.

The chain hooks the **forward** path, so it applies to traffic crossing the
router, not traffic addressed to the router itself.

## Step 3: Verify both outcomes

From h1:

```bash
curl -s http://<svc-link-address>/flag        # allowed
curl -s --max-time 2 http://<svc-link-address>:8080/status  # blocked
```

Expected: the flag returns, and the status port times out or refuses.

## Analysis

1. Why is the policy on the router rather than on the service?
2. What is the difference between the `input` and `forward` chains?
3. Why keep the default policy `accept` and add a specific drop in this lab?
4. How would you make the policy default-deny without breaking the flag?

## Defensive takeaway

A routed segment is the right enforcement point. Allow the service you intend to
expose, deny the rest, and test both the allowed and denied paths after every
change.
