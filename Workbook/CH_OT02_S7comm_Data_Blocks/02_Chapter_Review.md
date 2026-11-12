# OT02: Chapter Review

## Check Your Understanding

1. What port does S7comm use, and what does a successful connection prove?
2. What is a data block, and why does its layout matter in an incident review?
3. Why is segmentation the primary control for S7comm rather than a password?
4. Which evidence would you record for a DB read: host, DB number, offset, or
   all three?

## Lab Summary

| Exercise | Skill | Evidence |
|---|---|---|
| 2.1 | S7comm data-block read | DB1 marker at offset 32 |

## Defensive Checklist

- [ ] Control network segmented from the student and office networks
- [ ] TCP 102 blocked at the boundary
- [ ] Engineering access through a broker or VPN, not direct
- [ ] New TCP 102 sources alert to the SOC
- [ ] DB reads outside a maintenance window reviewed

## Next Step

Continue to the AI Security track, or return to the OT roadmap for the
OPC-UA and EtherNet/IP exercises when they are published.
