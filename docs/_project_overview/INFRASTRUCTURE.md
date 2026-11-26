# Infrastructure and component communications

Status: **current for release 5.56.1** (26 November 2026).

This page shows the runtime components and every communication path that matters
for operation, security review, and troubleshooting. It uses placeholders for
real addresses. The detailed internal addressing is in
[NETWORK-MAP.md](NETWORK-MAP.md).

## Runtime topology

```mermaid
flowchart TB
    subgraph Clients["Clients"]
        B["Desktop browser<br/>Vue SPA"]
        M["Mobile browser<br/>compact shell"]
        V["WireGuard client<br/>10.255.x.y/32"]
        LMS["LMS / IdP<br/>optional"]
    end

    subgraph Edge["ocr-frontend"]
        N["nginx<br/>:80 redirect, :443 SPA/API, :8443 wiki"]
        WV[("wiki_data<br/>read-only")]
    end

    subgraph App["ocr-backend"]
        API["FastAPI<br/>auth, RBAC, REST API"]
        CONSENT["Consent gate<br/>path matrix + revocation"]
        SCHED["Scheduler<br/>expiry, purge, cleanup"]
        ORCH["Lab orchestrator<br/>Docker Compose"]
        WSPROXY["RangeBox WebSocket proxy"]
        HA["Read-only HA snapshot reader"]
    end

    subgraph Data["Persistent data"]
        PG[("PostgreSQL 15<br/>users, labs, courses,<br/>completions, audit")]
        VK[("Valkey 9<br/>rate-limit counters")]
        WB[("workbook_data<br/>Exercise Studio")]
        BK[("backups_data<br/>database dumps")]
        HAS[("/var/lib/ocr-ha<br/>read-only status.json")]
    end

    subgraph Control["docker_control (internal)"]
        DSP["docker-socket-proxy<br/>:2375"]
        SOCK[("/var/run/docker.sock")]
    end

    subgraph Lab["Lab runtime"]
        DE["Docker Engine"]
        NET["Per-session bridge<br/>10.100.x.0/24"]
        TARGET["Lab targets"]
        RBOX["RangeBox desktop<br/>:6080"]
        TOPO["Topology links<br/>10.128.x /29"]
        SBOX["Standalone RangeBox<br/>10.50.x.0/24"]
    end

    subgraph VPN["VPN control plane"]
        PM["Peer Manager API<br/>host.docker.internal:5000"]
        WG["WireGuard wg0<br/>UDP 51820"]
    end

    subgraph Identity["Identity plane (optional)"]
        OIDC["Institution OIDC / SAML"]
        LDAP["LDAP / Active Directory"]
        DEX["Dex local test IdP"]
    end

    subgraph External["Optional external services"]
        SMTP["SMTP relay"]
        HIBP["HIBP range API<br/>admin opt-in"]
        GH["GitHub release API<br/>admin release check"]
    end

    B -->|HTTPS 443| N
    M -->|HTTPS 443| N
    B -->|wiki :8443| N
    N -->|/api HTTP| CONSENT
    CONSENT -->|allowed| API
    CONSENT -->|revoked| B
    N -->|auth subrequest| API
    N -->|static /wiki| WV
    API --> PG
    API --> VK
    API --> WB
    API --> BK
    API --> HAS
    API --> DSP
    DSP --> SOCK
    SCHED --> PG
    SCHED --> ORCH
    ORCH -->|Docker API| DE
    DE --> NET
    NET --> TARGET
    NET --> RBOX
    DE --> TOPO
    DE --> SBOX
    API -->|WebSocket proxy| RBOX
    V -->|UDP 51820| WG
    WG -.->|only the learner's /24| NET
    ORCH -->|peer add/remove| PM
    PM --> WG

    B <-->|OIDC/SAML redirect| OIDC
    API -->|token / JWKS / LDAP bind| OIDC
    API -->|LDAP bind| LDAP
    B -->|local test login| DEX
    API -->|SMTP| SMTP
    API -.->|SHA-1 prefix only| HIBP
    API -.->|release comparison| GH
    LMS -->|LTI launch / AGS / NRPS| N
```

## Communication matrix

| Source | Destination | Transport / port | Authentication and exposure | Purpose |
|---|---|---|---|---|
| Browser | `ocr-frontend` nginx | HTTPS `443/TCP`; WebSocket upgrade on `/api/rangebox/*` | Public edge; SPA login, Bearer token on API, short-lived VNC ticket | SPA, API, RangeBox desktop |
| Browser | `ocr-frontend` nginx | HTTPS `8443/TCP` | `wiki_session` HttpOnly cookie, validated by nginx `auth_request` | Workbook/wiki origin |
| Browser | `ocr-frontend` nginx | HTTP `80/TCP` | Redirect to HTTPS | Edge redirect |
| nginx | `ocr-backend` | HTTP `8000/TCP` on the Compose network; host binding `127.0.0.1:8000` | Internal only; CORS allowlist; trusted proxy headers | REST API, auth subrequests |
| nginx | `_wiki_auth` -> backend `/api/auth/me` | Internal subrequest | `wiki_session` cookie forwarded as Bearer | Validate wiki session |
| nginx | `_wiki_course_auth` -> backend `/api/auth/wiki-access` | Internal subrequest | Cookie plus course entitlement check | Course-only chapter gate |
| nginx | `_wiki_admin_auth` -> backend `/api/auth/wiki-admin-access` | Internal subrequest | Cookie plus admin role check | Admin wiki gate |
| nginx | `wiki_data` volume | Read-only filesystem | Mounted `:ro` | Serve generated MkDocs HTML |
| Backend | PostgreSQL `ocr-db` | PostgreSQL `5432/TCP` | App database role; parameterised SQL; TLS depends on deployment | Durable state |
| Backend | Valkey `ocr-valkey` | RESP `6379/TCP` | Private Compose network | Shared rate-limit counters |
| Backend | `ocr-docker-proxy` | HTTP `2375/TCP` on `docker_control` | Internal-only network; proxy is unauthenticated by design and reachable only by backend | Container/network/volume operations |
| Docker proxy | `/var/run/docker.sock` | Unix socket, read-only mount | Host control plane | Execute allowlisted Docker API calls |
| Backend | RangeBox websockify/Kasm | `ws://rangebox:6080` on session network | Backend validates a single-use WebSocket ticket; never exposed directly | noVNC/Kasm VNC stream |
| Backend | Peer Manager API | HTTP `host.docker.internal:5000` | `WG_API_KEY` | Add, remove, reconcile WireGuard peers |
| WireGuard client | Host `wg0` | UDP `51820` | Per-user peer key and `/32` client address | Reach only the learner's lab `/24` |
| Backend/scheduler | Lab containers | Docker API; tester traffic on session bridge | Orchestrator creates per-session project; no host networking | Spawn, health, teardown, tests |
| Backend | SMTP relay | SMTP `587/TCP` or configured port | Deployment credentials | Password reset and notifications |
| Backend | HIBP range API | HTTPS `443` | Admin opt-in; only first five SHA-1 characters leave the server | Password-breach range check |
| Backend | GitHub releases API | HTTPS `443` | Public read; admin release-status panel | Compare installed release with latest |
| LMS | nginx/backend | HTTPS `/api/lti/*` | LTI 1.3 signed launch, AGS/NRPS OAuth | Course launch, grade passback, roster |
| Backend | LMS (AGS/NRPS) | HTTPS `443` outbound | OAuth client credentials / LTI registration | Post scores and read the roster |
| Browser | Institution IdP | HTTPS redirect | OIDC/SAML | SSO login |
| Backend | IdP / LDAP / Dex | HTTPS / LDAPS / LDAP | Provider secrets encrypted at rest | Token exchange, JWKS, directory bind |
| Host collector | `/var/lib/ocr-ha/status.json` | Local file, read-only mount | Host-owned; no network API | Read-only HA card data |

## Request flows

### Login and ordinary API request

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser SPA
    participant N as nginx
    participant A as FastAPI
    participant P as PostgreSQL
    participant V as Valkey
    B->>N: POST /api/auth/login (TLS)
    N->>A: proxy /api
    A->>P: verify account and password hash
    A->>V: rate-limit counters
    A-->>B: access token + refresh token
    B->>N: GET /api/... Authorization: Bearer
    N->>A: proxy /api
    A->>P: scoped query
    A-->>B: JSON response
```

### Start a lab and open RangeBox

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant A as FastAPI
    participant D as Docker Engine
    participant L as Lab project
    participant R as RangeBox
    participant P as PostgreSQL
    B->>A: POST /api/labs/spawn/{slug}
    A->>D: create session network + Compose project
    D->>L: start target containers
    D->>R: start RangeBox on the session bridge
    A->>P: store session, network subnet, project
    A-->>B: session id / spawn status
    B->>A: POST /api/rangebox/ws-ticket
    A-->>B: single-use ticket
    B->>A: WebSocket /api/rangebox/{session}/vnc?token=...
    A->>R: proxy to websockify/Kasm :6080
    R-->>B: framebuffer + input
```

### Workbook/wiki request

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant N as nginx
    participant A as FastAPI
    participant W as wiki_data
    B->>N: GET /wiki/range/... or :8443
    N->>A: auth_request /_wiki_auth
    A-->>N: 200 / 401 / 403
    alt authorised
        N->>W: read-only file
        W-->>B: HTML/assets
    else unauthorised
        N-->>B: redirect to login or course list
    end
```

### VPN configuration and lab access

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant A as FastAPI
    participant P as Peer Manager
    participant W as WireGuard wg0
    participant L as Learner lab /24
    B->>A: GET /api/labs/vpn-config
    A->>A: allocate client /32, encrypt private key
    A->>P: add peer with allowed_ips = learner /32
    P->>W: apply peer
    A-->>B: WireGuard config file
    B->>W: UDP 51820 handshake
    W->>L: route only to the learner's session /24
```

### LTI launch and grade passback

```mermaid
sequenceDiagram
    autonumber
    participant M as Moodle/LMS
    participant N as nginx
    participant A as FastAPI
    participant P as PostgreSQL
    M->>N: OIDC login / launch
    N->>A: /api/lti/*
    A->>P: link account, course, assignment
    A-->>M: launch response / Deep Linking
    A->>M: AGS score + NRPS roster (outbound)
```

## Trust boundaries and least privilege

- **Public edge:** only nginx publishes `80`, `443`, and `8443`. The backend is
  bound to `127.0.0.1:8000`, and PostgreSQL/Valkey are not published.
- **Docker control:** `docker_control` is an internal Compose network. Only the
  backend and the socket proxy join it; the frontend, database, cache, and lab
  containers do not.
- **Lab isolation:** each session gets its own bridge and `/24`; no cross-session
  routing. Lab containers have no host networking, no Docker socket, and no
  privileged mode.
- **VPN:** a learner gets a `/32` client address and a route only to their own
  session `/24`. Firewall rules drop lab/RangeBox subnets from external
  interfaces.
- **Wiki:** the wiki volume is read-only in the frontend; nginx calls backend
  auth subrequests before serving any protected page.
- **Consent:** the consent gate runs before the API for covered paths and
  returns `403` when revoked.
- **HA:** the backend reads a host-written snapshot; it never promotes, fails
  over, or writes the witness state.

## Related

- [NETWORK-MAP.md](NETWORK-MAP.md) for addresses, Docker networks, and ports.
- [SOFTWARE-METADATA.md](SOFTWARE-METADATA.md) for versions and latest releases.
- [API-CAPABILITIES.md](API-CAPABILITIES.md) and [openapi.json](openapi.json) for the API contract.
