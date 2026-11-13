# Exercise 2.9: Active Directory Fundamentals

## Goal

Bind with a standard helpdesk account and enumerate the directory: users,
groups, and the service account whose description leaks a credential and the
case token.

## Step 1: Understand the namespace

| Item | Value |
|---|---|
| Domain | `LAB` |
| Base DN | `dc=lab,dc=example,dc=org` |
| Users | `ou=People` |
| Groups | `ou=Groups` |
| Your account | `uid=analyst,ou=People,dc=lab,dc=example,dc=org` |

A distinguished name is the full path to an object. `uid=analyst` alone is not
enough to bind unless the server is configured to resolve it.

## Step 2: Bind and enumerate

```bash
ldapsearch -x -H ldap://<directory-ip> \
  -D 'uid=analyst,ou=People,dc=lab,dc=example,dc=org' \
  -w 'Analyst2026' \
  -b 'dc=lab,dc=example,dc=org' \
  '(objectClass=inetOrgPerson)' cn uid description
```

Record the users and any descriptions.

## Step 3: Find the service account

```bash
ldapsearch -x -H ldap://<directory-ip> \
  -D 'uid=analyst,ou=People,dc=lab,dc=example,dc=org' \
  -w 'Analyst2026' \
  -b 'dc=lab,dc=example,dc=org' \
  '(uid=svc-backup)' description
```

The description contains a password and the case token. A service account should
never store either in a readable attribute.

## Step 4: Check group membership

```bash
ldapsearch -x -H ldap://<directory-ip> \
  -D 'uid=analyst,ou=People,dc=lab,dc=example,dc=org' \
  -w 'Analyst2026' \
  -b 'ou=Groups,dc=lab,dc=example,dc=org' \
  '(objectClass=groupOfNames)' cn member
```

Group membership is part of identity. The helpdesk account and the service
account should not share a privileged group.

## Analysis

1. Why is the full DN required for the bind?
2. What is the risk of a password in `description`?
3. Which group would you review first for privilege?
4. How does Kerberos change the authentication flow in a real AD domain?

## Defensive takeaway

Directory descriptions are data. Treat them as untrusted, alert on service
accounts with credentials in readable attributes, and use managed service
accounts with rotation.
