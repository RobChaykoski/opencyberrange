# Exercise 2.3: YARA Incident Triage

## Goal

Identify the matching artifact with YARA, then correlate its marker in the
incident log to recover the case token.

## Step 1: Scan the evidence

```bash
cat > /tmp/beacon.yar <<'EOF'
rule beacon {
  strings:
    $a = "HALCYON-BEACON"
  condition:
    $a
}
EOF
yara /tmp/beacon.yar /evidence
```

Expected: `payload.bin`. `readme.txt` is the control.

## Step 2: Correlate the log

```bash
grep HALCYON-BEACON /var/log/incident.log
```

The log line names the host, process, file, marker, action, and case token.

Expected token: `OCR{y4r4_m33ts_l0g5}`.

## Step 3: Write the evidence note

| Field | Value |
|---|---|
| Host | |
| File | |
| Marker | |
| Process | |
| Action | |
| Log timestamp | |

Do not put the token in a shared document.

## Analysis

1. What does the YARA match prove, and what does it not prove?
2. Which log fields turn the match into a finding?
3. Why is the control file useful?
4. What would you check next if the log showed a different process?

## Defensive takeaway

A match is a lead. Correlate the file marker with process and response logs,
record the evidence, and keep the verdict proportional to what you can prove.
