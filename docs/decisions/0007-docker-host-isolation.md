# 0007: Isolate the Docker lab control plane from the web tier

Status: **accepted for a spike**; production cutover pending validation
Date: 24 November 2026

## Context

The backend creates lab containers through the host Docker API and runs
short-lived privileged or host-network helper containers for route detection,
firewall isolation, GRETAP bridging, and TC mirrors. The helper image is now
pre-baked and digest-pinned, so helpers no longer install packages at runtime.
The trust boundary is unchanged: a compromised backend can reach the Docker
socket and is effectively host-root.

The platform is a single-host teaching appliance today. Multi-tenancy and HA are
future work. Both would inherit this boundary if it is not separated first.

## Options

| Option | Security property | Cost | Assessment |
|---|---|---|---|
| 1. Status quo plus socket proxy | Backend still reaches a broad Docker API; a proxy filter reduces but does not remove host-root blast radius | Low | Not sufficient for multi-tenant or internet-facing deployments |
| 2. Pre-baked helpers plus a tightly restricted socket proxy | Runtime package installs are gone; the backend can still create privileged and host-network containers | Medium | Good interim; already partly implemented |
| 3. Host-side agent (`ocr-labd`) with a narrow authenticated API | Only the agent has host network/Docker control; the web tier has no Docker socket | Medium-high | **Recommended target** |
| 4. Rootless Docker or Podman | Stronger runtime isolation; lab network features need validation | High | Evaluate after the agent boundary |
| 5. Kubernetes or containerd | Strong scheduling and isolation, but a major operational shift | Very high | Out of scope for the single-host appliance |

## Recommendation

Adopt **option 3** as the target architecture, with **option 2** kept as the
interim state.

The agent should expose only the operations the platform needs:

- `spawn(lab, user, session, network)` and `stop(session)`;
- `status(session)` and resource usage;
- `ensure_isolation(source_ranges, host_lan)`;
- `mirror_gretap(session, interface)`;
- `logs(session, cursor)`.

It must not expose arbitrary `exec`, image build, volume mount, or host
filesystem operations.

## Decision

Accepted for a spike on 24 November 2026. The skeleton lives in
`platform/labd/`. `GET /v1/status/<lab_id>` is implemented read-only with a
validated id and a fixed `docker inspect`, and has been checked against a live
container on development; mutating routes still return `501`.
Production keeps the pre-baked helper image and restricted socket proxy until
the lab harness passes on network, ICS, and RangeBox labs.

## Security properties

- The web/backend containers no longer mount or reach `/var/run/docker.sock`.
- The agent authenticates the backend with a short-lived token or mTLS and
  authorizes by operation and tenant.
- The agent owns the privileged network namespace and firewall rules.
- Lab image names and compose files are validated by the agent, not trusted from
  the request.
- Every operation is audited with the actor, session, lab, and outcome.

## Migration plan

1. Define the agent API and the request/response schema.
2. Implement the agent as a small host service with a systemd unit and a
   dedicated Unix socket or loopback TLS endpoint.
3. Move route detection, isolation rules, GRETAP, and TC mirroring behind the
   agent first; these are the privileged helper calls.
4. Move spawn/stop/status next. Keep the Docker SDK path behind a feature flag
   for one release.
5. Remove the Docker socket mount and the socket-proxy dependency from the
   backend.
6. Run the lab harness against network, ICS, and RangeBox labs before removing
   the fallback.

## Open questions

- Agent implementation language and packaging.
- Authentication: Unix socket peer credentials, mTLS, or a short-lived token.
- How the agent reports asynchronous build progress.
- HA behavior when two hosts share a database.
- Whether rootless Docker or Podman can replace the privileged helper entirely.

## References

- [Security review log](../SECURITY-REVIEW-2026-11-24.md)
- [Code and database review](../CODE-AND-DATABASE-REVIEW-2026-11-24.md)
- `platform/backend/app/services/docker_manager.py`
- `scripts/deploy-inplace.sh`
- `platform/netprobe/Dockerfile`
