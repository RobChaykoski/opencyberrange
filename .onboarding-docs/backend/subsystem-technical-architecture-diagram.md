# Backend technical architecture

```mermaid
flowchart TB
    subgraph Edge["nginx (frontend container)"]
        Proxy["/api reverse proxy"]
    end

    subgraph Middleware["Starlette middleware"]
        ReqId["Request id + security events"]
        Consent["Consent enforcement<br/>path -> consent domain"]
        Imp["Impersonation guard"]
        Labels["Export data labels"]
        CORS["CORS"]
    end

    subgraph Routers["FastAPI routers"]
        AuthR["auth"]
        AdminR["admin / security_admin / governance"]
        CourseR["courses / instructor / curriculum"]
        LabR["labs / rangebox / exercise_tester"]
        LearnR["quiz / practice / evidence / capstones"]
        AnalyticsR["analytics / dashboard / reports / profile"]
        IntegR["sso / lti / identity / about"]
    end

    subgraph Deps["Dependencies"]
        CurrentUser["get_current_user"]
        Active["get_current_active_user"]
        Role["role / permission dependency"]
        Tenant["tenant + RLS context"]
        Reauth["recent reauth"]
    end

    subgraph Services["Domain services"]
        AuthS["auth_sessions, reauth, mfa, password_reset"]
        AuthzS["rbac, authorization, access_matrix, policy_context"]
        LabS["docker_manager, lab_preflight, rangebox_capacity, topology_engine"]
        LearnS["evidence, competency_*, scoring, achievements, practice"]
        ReportS["analytics_report, pdf_report, report_integrity, export_labels"]
        ConsentS["consent service, erasure, erasure_ledger, suppression"]
        DnaS["dna_events, skill_dna, cyber_gps"]
        IntegS["oidc, saml_auth, ldap_auth, lti"]
        SchedS["scheduler"]
    end

    subgraph Stores["Data and external systems"]
        PG[("PostgreSQL")]
        Valkey[("Valkey")]
        Work[("workbook_data")]
        Backups[("backups_data")]
        Docker["docker-socket-proxy"]
        IdP["OIDC / SAML / LDAP"]
        GRC["OpenGRC"]
    end

    Proxy --> ReqId --> Consent --> Imp --> Labels --> CORS --> Routers
    Routers --> Deps
    Deps --> Services
    Services --> PG
    Services --> Valkey
    Services --> Work
    Services --> Backups
    LabS --> Docker
    IntegS --> IdP
    ReportS --> GRC
    SchedS --> PG
    SchedS --> Docker
```

## Layering rules

| Layer | May depend on | Must not |
|---|---|---|
| Router | schemas, dependencies, services | contain domain rules or raw SQL |
| Dependency | auth, permissions, tenant | make business decisions |
| Service | models, other services, data files | depend on HTTP request objects |
| Model | SQLAlchemy only | call services or routers |
| Data file | nothing | be edited at runtime |

## Cross-cutting order

1. **Authentication** — decode the JWT, check `sec`, bind the session, load the
   user.
2. **Authorization** — role and permission dependencies, tenant scope, policy
   attributes.
3. **Consent** — middleware block for gated paths before the service runs.
4. **Validation** — Pydantic schemas and input-safety normalisation.
5. **Domain** — service method, transaction, ledger trigger.
6. **Serialisation** — response schema and export labels.

## Related

- [Backend overview](subsystem-overview.md)
- [Feature index](features/README.md)
- [Database](../database/subsystem-overview.md)
- [Cache](../cache/subsystem-overview.md)
- [Docker control](../docker-proxy/subsystem-overview.md)
