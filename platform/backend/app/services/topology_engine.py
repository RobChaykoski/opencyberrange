"""Expand a lab's ``x-ocr-topology`` block into Docker networks and env.

The engine is deliberately data-only. A lab declares nodes and point-to-point
links; the engine allocates a private /29 for each link, assigns the two
endpoints, and gives each node a JSON description of its interfaces. It never
accepts a privileged container, a host network, a bind mount, or an arbitrary
image.

Switch note: this MVP represents an L2 segment with the Docker bridge that
already backs each link. A dedicated switch container (with a multi-port bridge
and a shared broadcast domain) is a later increment; the engine does not claim
one here.
"""

from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass

TOPOLOGY_KEY = "x-ocr-topology"
NODE_IMAGE_PREFIX = "ocr-lab/topology-node"
NODE_ROLES = {"router", "host", "service"}
MAX_NODES = 12
MAX_LINKS = 24
RESERVED_ENV_PREFIX = "OCR_"

_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")


class TopologyError(ValueError):
    """A lab topology is unsafe or malformed."""


@dataclass(frozen=True)
class Link:
    index: int
    from_id: str
    to_id: str
    subnet: ipaddress.IPv4Network
    from_ip: str
    to_ip: str


def _as_dict(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise TopologyError(f"{label} must be a mapping")
    return value


def _node_spec(raw, node_id: str) -> dict:
    spec = _as_dict(raw, f"topology node {node_id!r}")
    service = str(spec.get("service") or "").strip()
    role = str(spec.get("role") or "").strip().lower()
    if not service:
        raise TopologyError(f"topology node {node_id!r} needs a service")
    if role not in NODE_ROLES:
        raise TopologyError(
            f"topology node {node_id!r} role must be one of {sorted(NODE_ROLES)}"
        )
    unknown = set(spec) - {
        "service",
        "role",
        "flag",
        "http_port",
        "routes",
        "description",
    }
    if unknown:
        raise TopologyError(
            f"topology node {node_id!r} has unsupported keys: {sorted(unknown)}"
        )
    return {**spec, "service": service, "role": role}


def _validate_service(compose_data: dict, service_name: str, node_id: str) -> None:
    services = _as_dict(compose_data.get("services") or {}, "compose services")
    service = services.get(service_name)
    if not isinstance(service, dict):
        raise TopologyError(
            f"topology node {node_id!r} points at missing service {service_name!r}"
        )

    image = str(service.get("image") or "")
    if not image.startswith(NODE_IMAGE_PREFIX):
        raise TopologyError(
            f"topology service {service_name!r} must use {NODE_IMAGE_PREFIX}*"
        )
    for forbidden in ("build", "privileged", "network_mode", "pid", "ipc", "devices", "volumes"):
        if service.get(forbidden):
            raise TopologyError(
                f"topology service {service_name!r} must not set {forbidden}"
            )
    if service.get("security_opt") and "no-new-privileges:true" not in service.get(
        "security_opt", []
    ):
        raise TopologyError(
            f"topology service {service_name!r} security_opt must keep no-new-privileges"
        )
    caps = set(service.get("cap_add") or [])
    if caps - {"NET_ADMIN", "NET_RAW"}:
        raise TopologyError(
            f"topology service {service_name!r} may only add NET_ADMIN and NET_RAW"
        )
    labels = service.get("labels") or {}
    if str(labels.get("ocr_lab_net", "true")).lower() == "false":
        raise TopologyError(
            f"topology service {service_name!r} must stay on the lab network"
        )
    if not str(labels.get("ip_offset", "")).strip():
        raise TopologyError(
            f"topology service {service_name!r} needs an ip_offset label"
        )
    for key in (service.get("environment") or {}):
        if str(key).startswith(RESERVED_ENV_PREFIX):
            raise TopologyError(
                f"topology service {service_name!r} may not set {key}; the engine owns it"
            )


def _link_subnet(second_octet: int, third_octet: int, index: int) -> ipaddress.IPv4Network:
    # 10.128.0.0/9 is already a protected lab range. Stay below 10.200 so the
    # RangeBox proxy range can never be selected.
    base_second = 128 + ((second_octet - 100) % 72)
    return ipaddress.ip_network(
        f"10.{base_second}.{third_octet}.{index * 8}/29", strict=False
    )


def expand(
    compose_data: dict,
    *,
    user_id: int,
    lab_slug: str,
    second_octet: int,
    third_octet: int,
) -> dict:
    """Return ``networks``, ``service_networks``, ``service_env``, ``service_sysctls``.

    An empty topology returns empty maps so the caller can treat it as a no-op.
    """
    if not isinstance(compose_data, dict):
        return {}
    raw = compose_data.get(TOPOLOGY_KEY)
    if raw is None:
        return {}
    spec = _as_dict(raw, TOPOLOGY_KEY)

    unknown = set(spec) - {"nodes", "links", "training_user", "training_password"}
    if unknown:
        raise TopologyError(f"{TOPOLOGY_KEY} has unsupported keys: {sorted(unknown)}")

    nodes_raw = _as_dict(spec.get("nodes") or {}, "topology nodes")
    links_raw = spec.get("links") or []
    if not nodes_raw:
        raise TopologyError("topology needs at least one node")
    if len(nodes_raw) > MAX_NODES:
        raise TopologyError(f"topology supports at most {MAX_NODES} nodes")
    if not isinstance(links_raw, list) or not links_raw:
        raise TopologyError("topology needs at least one link")
    if len(links_raw) > MAX_LINKS:
        raise TopologyError(f"topology supports at most {MAX_LINKS} links")

    nodes = {}
    used_services: set[str] = set()
    for node_id, node_raw in nodes_raw.items():
        node_id = str(node_id).lower()
        if not _ID_RE.match(node_id):
            raise TopologyError(f"invalid topology node id {node_id!r}")
        node = _node_spec(node_raw, node_id)
        if node["service"] in used_services:
            raise TopologyError(
                f"two topology nodes point at service {node['service']!r}"
            )
        used_services.add(node["service"])
        _validate_service(compose_data, node["service"], node_id)
        nodes[node_id] = node

    links: list[Link] = []
    for index, raw_link in enumerate(links_raw):
        link = _as_dict(raw_link, f"topology link {index}")
        unknown = set(link) - {"from", "to", "label"}
        if unknown:
            raise TopologyError(f"topology link {index} has unsupported keys: {sorted(unknown)}")
        from_id = str(link.get("from") or "").strip().lower()
        to_id = str(link.get("to") or "").strip().lower()
        if from_id not in nodes or to_id not in nodes:
            raise TopologyError(
                f"topology link {index} must reference known nodes"
            )
        if from_id == to_id:
            raise TopologyError(f"topology link {index} cannot connect a node to itself")
        if any({l.from_id, l.to_id} == {from_id, to_id} for l in links):
            raise TopologyError(f"topology link {index} is a duplicate")
        subnet = _link_subnet(second_octet, third_octet, index)
        # .1 is the Docker gateway, .2 and .3 are the endpoints.
        links.append(
            Link(
                index=index,
                from_id=from_id,
                to_id=to_id,
                subnet=subnet,
                from_ip=str(subnet.network_address + 2),
                to_ip=str(subnet.network_address + 3),
            )
        )

    networks: dict[str, dict] = {}
    service_networks: dict[str, dict] = {}
    service_env: dict[str, dict] = {}
    service_sysctls: dict[str, dict] = {}

    for link in links:
        name = f"topo_{link.index}"
        networks[name] = {
            "driver": "bridge",
            "labels": {"ocr.topology": "true"},
            "ipam": {
                "config": [
                    {
                        "subnet": str(link.subnet),
                        "gateway": str(link.subnet.network_address + 1),
                    }
                ]
            },
        }

    node_links: dict[str, list[dict]] = {node_id: [] for node_id in nodes}
    for link in links:
        node_links[link.from_id].append(
            {
                "peer": link.to_id,
                "peer_service": nodes[link.to_id]["service"],
                "ip": link.from_ip,
                "peer_ip": link.to_ip,
                "subnet": str(link.subnet),
            }
        )
        node_links[link.to_id].append(
            {
                "peer": link.from_id,
                "peer_service": nodes[link.from_id]["service"],
                "ip": link.to_ip,
                "peer_ip": link.from_ip,
                "subnet": str(link.subnet),
            }
        )

    training_user = str(spec.get("training_user") or "analyst")
    training_password = str(spec.get("training_password") or "")
    if not training_password:
        raise TopologyError("topology needs training_password")
    if len(training_password) < 10:
        raise TopologyError("topology training_password must be at least 10 characters")

    for node_id, node in nodes.items():
        service = node["service"]
        my_links = node_links[node_id]
        if not my_links:
            raise TopologyError(f"topology node {node_id!r} is not connected to a link")

        env = {
            "OCR_NODE_ID": node_id,
            "OCR_ROLE": node["role"],
            "OCR_LINKS": json.dumps(my_links, sort_keys=True),
            "OCR_SSH_USER": training_user,
            "OCR_SSH_PASSWORD": training_password,
        }
        if node["role"] == "router":
            service_sysctls[service] = {"net.ipv4.ip_forward": 1}
        if node["role"] in {"host", "service"}:
            router_links = [
                item
                for item in my_links
                if nodes[item["peer"]]["role"] == "router"
            ]
            if router_links:
                env["OCR_GATEWAY"] = router_links[0]["peer_ip"]
        if node.get("routes"):
            resolved = []
            for route in node["routes"]:
                route = _as_dict(route, f"topology route on {node_id!r}")
                to = str(route.get("to") or "").strip()
                via = str(route.get("via") or "").strip()
                if not to or not via:
                    raise TopologyError(
                        f"topology route on {node_id!r} needs to and via"
                    )
                if via not in nodes:
                    raise TopologyError(
                        f"topology route on {node_id!r} references unknown node {via!r}"
                    )
                peer = next(
                    (item for item in my_links if item["peer"] == via), None
                )
                if peer is None:
                    raise TopologyError(
                        f"topology route on {node_id!r} uses {via!r}, which is not a direct peer"
                    )
                resolved.append({"to": to, "via": peer["peer_ip"]})
            env["OCR_ROUTES"] = json.dumps(resolved)
        if node.get("flag"):
            if node["role"] != "service":
                raise TopologyError("only a service node may declare a flag")
            env["OCR_FLAG"] = str(node["flag"])
        if node.get("http_port"):
            env["OCR_HTTP_PORT"] = str(int(node["http_port"]))

        service_env[service] = env
        service_networks[service] = {
            f"topo_{link.index}": {"ipv4_address": link.from_ip if link.from_id == node_id else link.to_ip}
            for link in links
            if node_id in {link.from_id, link.to_id}
        }

    return {
        "networks": networks,
        "service_networks": service_networks,
        "service_env": service_env,
        "service_sysctls": service_sysctls,
        "nodes": nodes,
        "links": links,
        "lab_slug": lab_slug,
        "user_id": user_id,
    }
