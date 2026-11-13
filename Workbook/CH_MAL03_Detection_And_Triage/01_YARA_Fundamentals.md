# Exercise 2.2: YARA Fundamentals

## Goal

Write a string rule, scan three benign samples, and recover the case token from
the matching report.

## Step 1: Confirm the tool

```bash
ssh analyst@<target-ip>
yara --version
```

## Step 2: Write the rule

```bash
cat > /tmp/beacon.yar <<'EOF'
rule beacon {
  strings:
    $a = "HALCYON-BEACON"
  condition:
    $a
}
EOF
```

A rule has a name, optional strings, and a condition. This rule matches any file
that contains the marker.

## Step 3: Scan the samples

```bash
yara /tmp/beacon.yar /samples
```

Expected: only `report.txt` matches. The invoice and notes are controls.

## Step 4: Recover the token

```bash
cat /samples/report.txt
```

Expected: `OCR{y4r4_rul3s_4nd_3v1d3nc3}`.

## Analysis

1. What does the condition `$a` mean?
2. Why is it useful to scan a file that should not match?
3. How could an attacker evade this rule without changing behaviour?
4. What evidence would you add before calling the file malicious?

## Defensive takeaway

String rules are fast and explainable, but brittle. Pair YARA with behavioural,
process, and network evidence before making a verdict.
