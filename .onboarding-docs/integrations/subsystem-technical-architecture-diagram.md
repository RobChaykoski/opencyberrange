# Integration technical architecture

```mermaid
flowchart LR
    subgraph OCR["OpenCyberRange"]
        API["FastAPI"]
        Evidence["Evidence and reports"]
        SSO["SSO adapters"]
        LTI["LTI 1.3"]
    end

    subgraph Identity["Identity"]
        Authentik["Authentik<br/>operational SSO"]
        Institution["Institution IdP<br/>OIDC / SAML / LDAP"]
        OpenIAM["OpenIAM<br/>identity governance"]
    end

    subgraph Learning["Learning"]
        Moodle["Moodle<br/>LTI consumer"]
    end

    subgraph GRC["Governance and security"]
        OpenGRC["OpenGRC<br/>GRC system of record"]
        ODE["OpenDetectionEngine / OpenDLP"]
        Dojo["DefectDojo"]
    end

    subgraph Ops["Operations"]
        Prom["Prometheus / Grafana"]
    end

    API -->|OIDC / SAML / LDAP| Authentik
    API -->|OIDC / SAML / LDAP| Institution
    API <-->|role and lifecycle evidence| OpenIAM
    API <-->|LTI 1.3 launch / deep link| Moodle
    Evidence -->|aggregate, hashed| OpenGRC
    ODE -->|classification evidence| OpenGRC
    Dojo -->|finding references| OpenGRC
    API -->|/metrics| Prom
```

## Boundary rules

| Boundary | Send | Never send |
|---|---|---|
| OpenGRC | aggregate counts, control references, stable IDs, hashes, periods | learner rows, PCAP, payloads |
| Moodle | LTI launch context, assignment reference, grade passback where configured | full learner record |
| Identity provider | subject, email, display name, role mapping | password, MFA secret |
| OpenIAM | role and lifecycle evidence | learner academic record |
| Monitoring | service metrics and status | learner identifiers or content |

## Related

- [Ecosystem map](../../docs/ECOSYSTEM-TOOLING-MAP.md)
- [Reporting roadmap](../../docs/REPORTING-ROADMAP.md)
- [OpenGRC](opengrc/README.md)
