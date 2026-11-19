# IR lab: OAuth consent to cloud storage

**Azure concept:** an attacker consents a malicious Entra ID application, then
uses the delegated token to read a storage account.

**Local simulation:** Keycloak consent event, MinIO object reads, OpenSearch
events, and Vault secret access.

**Goal:** investigate the consent, identify persistence, revoke the session and
consent, and write a report.

## Scenario

A learner opens a phishing email offering an invoice. The link starts an OAuth
consent flow for `invoice-sync`, a look-alike application. The learner approves
it. Minutes later, a synthetic service principal lists and reads objects in the
`patient-data` bucket from an unfamiliar address.

The learner is the on-call analyst. They must:

1. review the sign-in, consent, token, storage, and secret events;
2. identify the application, scopes, and persistence;
3. determine what data the token could reach;
4. revoke the consent and sessions;
5. preserve the timeline and evidence;
6. write a technical finding and a one-page executive summary.

## Local mapping

| Azure concept | Local service |
|---|---|
| Entra ID sign-in and audit | Keycloak events, `cloud-events` index |
| OAuth application consent | Keycloak client consent |
| Delegated token | Keycloak access and refresh tokens |
| Blob storage | MinIO `patient-data` bucket |
| Key Vault | Vault `secret/healthcare-prod/app` |
| Sentinel | OpenSearch Dashboards |
| Session revocation | Keycloak logout and token revocation |

Keycloak is not Entra ID. The lab simulates OIDC consent, scopes, groups, and
session revocation. Conditional Access and Entra-specific signals are out of
scope.

## Prerequisites

- core stack running (Keycloak, MinIO, Vault, OpenSearch);
- `cloud-events` index seeded from `datasets/cloud-events.ndjson`;
- `patient-data` bucket with synthetic files;
- `invoice-sync` client in the realm, or a learner-created client with the same
  name.

## Tasks

1. **Scope the event.** Query `cloud-events` for `student` between 08:00 and
   10:00. List the sign-in, consent, token, storage, and secret events.
2. **Identify the application.** Which client received consent? Which scopes
   were granted? Is it an approved client?
3. **Find the persistence.** What token allows continued access after the first
   read? Does revoking the session revoke the refresh token?
4. **Measure the impact.** Which objects were read? Were any secrets accessed?
5. **Contain.** Disable the client, revoke the user's sessions, rotate the
   secret if it was read.
6. **Verify.** Attempt the old token and confirm it fails.
7. **Preserve evidence.** Export the event list, token IDs, object list, and
   secret version.
8. **Report.** Technical finding plus executive summary with impact, decision,
   and next action.

## Evidence

- event timeline with source IPs and application IDs;
- consent and scope record;
- list of objects read;
- revocation record and before/after token test;
- secret rotation record if applicable;
- technical report and executive summary.

## Rubric

| Dimension | Weight |
|---|---:|
| Timeline and evidence quality | 30% |
| Correct application and scope identification | 20% |
| Containment and revocation | 20% |
| Impact assessment | 15% |
| Executive summary | 15% |

## Reset

1. Delete the `invoice-sync` client or revoke its consent.
2. Revoke the learner's sessions and refresh tokens.
3. Recreate the `patient-data` bucket contents.
4. Restore the Vault secret version.
5. Re-seed `cloud-events` if the learner deleted documents.

## Safety

- Synthetic users, objects, and secrets only.
- No real OAuth provider, token, or cloud account.
- Do not send the phishing email outside the lab network.
