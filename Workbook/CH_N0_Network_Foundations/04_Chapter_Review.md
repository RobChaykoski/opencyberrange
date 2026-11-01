# CH N0 -- Chapter Review

## What You Learned

- A host has an IP address; people use names; DNS maps one to the other.
- `ping` uses ICMP echo requests and replies. It proves host reachability, not
  service availability.
- DNS publishes several record types, including A, CNAME, MX, and TXT.
- TTL controls caching, so a changed record can take time to appear.
- Troubleshooting works down the layers: **name -> host -> service**.
- Every tool answers a different question, and no single tool answers all of
  them.

## Self-Assessment

Answer these without looking back. Then check your notes.

1. What protocol does `ping` use?
2. What does a 0% packet loss result prove?
3. What does it not prove?
4. What is the difference between an A record and a CNAME?
5. What is a TXT record commonly used for?
6. What does TTL control?
7. Why is DNS a trust boundary?
8. A user says "the site is down." What are the first three layers you check?
9. If the name resolves to the right address but ping fails, what might be wrong?
10. If ping succeeds but the web page fails, what might be wrong?

## Command Cheat Sheet

### Ping

```bash
ping -c 4 <host>          # Linux/macOS: four requests
ping -n 4 <host>          # Windows: four requests
```

### DNS

```bash
dig @<server> <name> A
dig @<server> <name> CNAME
dig @<server> <name> MX
dig @<server> <name> TXT
dig @<server> <name> A +short
nslookup <name> <server>
host <name> <server>
```

### Service check

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://<host>/
curl -s http://<host>/
```

## Layer Checklist

| Layer | Check | If it fails |
|---|---|---|
| Name | `dig` / `nslookup` | Check the record, the zone, and the resolver |
| Host | `ping` | Check the address, route, and firewall |
| Service | `curl` / browser | Check the port, process, and application logs |

## Reflection

Write two or three sentences answering:

> What is the most useful thing you learned about troubleshooting in this
> chapter, and how would you explain it to a non-technical user?

## Next Chapter

**CH N1 -- Log Analysis** shows how the events you generated in these labs appear
in firewall and DNS logs.
