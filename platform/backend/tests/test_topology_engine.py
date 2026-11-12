"""Unit tests for the network-device topology engine.

The engine is pure data validation/expansion, so these tests do not need Docker.
They cover the safety boundary: an unsafe topology must fail before a container
is created.
"""

from __future__ import annotations

import ipaddress
import json

import pytest

from app.services import topology_engine


def _node(image="ocr-lab/topology-node:latest", **overrides):
    service = {
        "image": image,
        "labels": {"ip_offset": "21"},
        "cap_add": ["NET_ADMIN"],
        "security_opt": ["no-new-privileges:true"],
    }
    service.update(overrides)
    return service


def _compose(nodes=None, links=None, extra=None):
    nodes = nodes or {
        "h1": {"service": "h1", "role": "host"},
        "r1": {"service": "r1", "role": "router"},
        "svc": {
            "service": "svc",
            "role": "service",
            "flag": "OCR{topology}",
            "http_port": 80,
        },
    }
    links = links or [{"from": "h1", "to": "r1"}, {"from": "r1", "to": "svc"}]
    spec = {
        "training_user": "analyst",
        "training_password": "Topology2026!",
        "nodes": nodes,
        "links": links,
    }
    if extra:
        spec.update(extra)
    return {
        "services": {
            "h1": _node(),
            "r1": _node(labels={"ip_offset": "22"}),
            "svc": _node(labels={"ip_offset": "23"}),
        },
        "x-ocr-topology": spec,
    }


def _expand(compose, **overrides):
    values = {
        "user_id": 7,
        "lab_slug": "network-12-2-device-topology-engine",
        "second_octet": 100,
        "third_octet": 7,
    }
    values.update(overrides)
    return topology_engine.expand(compose, **values)


def test_absent_topology_is_a_no_op():
    assert _expand({"services": {}}) == {}


def test_valid_topology_allocates_links_and_gateways():
    result = _expand(_compose())

    assert set(result["networks"]) == {"topo_0", "topo_1"}
    for network in result["networks"].values():
        subnet = ipaddress.ip_network(
            network["ipam"]["config"][0]["subnet"], strict=False
        )
        assert str(subnet).endswith("/29")
        assert str(subnet).startswith("10.128.7.")
        assert network["ipam"]["config"][0]["gateway"] == str(
            subnet.network_address + 1
        )

    assert result["service_networks"]["h1"]["topo_0"]["ipv4_address"] == "10.128.7.2"
    assert result["service_networks"]["r1"]["topo_0"]["ipv4_address"] == "10.128.7.3"
    assert result["service_networks"]["r1"]["topo_1"]["ipv4_address"] == "10.128.7.10"
    assert result["service_networks"]["svc"]["topo_1"]["ipv4_address"] == "10.128.7.11"

    h1_env = result["service_env"]["h1"]
    links = json.loads(h1_env["OCR_LINKS"])
    assert links[0]["peer"] == "r1"
    assert h1_env["OCR_GATEWAY"] == links[0]["peer_ip"]
    assert result["service_sysctls"]["r1"] == {"net.ipv4.ip_forward": 1}
    assert result["service_env"]["svc"]["OCR_FLAG"] == "OCR{topology}"
    assert "OCR_GATEWAY" in result["service_env"]["svc"]


def test_router_does_not_get_a_default_gateway():
    result = _expand(_compose())
    assert "OCR_GATEWAY" not in result["service_env"]["r1"]


def test_static_route_resolves_a_direct_peer():
    compose = _compose()
    compose["x-ocr-topology"]["nodes"]["r1"]["routes"] = [
        {"to": "10.20.20.0/24", "via": "svc"}
    ]
    result = _expand(compose)
    routes = json.loads(result["service_env"]["r1"]["OCR_ROUTES"])
    assert routes[0]["to"] == "10.20.20.0/24"
    assert routes[0]["via"] == result["service_networks"]["svc"]["topo_1"]["ipv4_address"]


def test_link_subnets_stay_inside_the_protected_range():
    for user_id, second in ((7, 100), (300, 100), (554, 101), (2000, 107)):
        result = _expand(
            _compose(),
            user_id=user_id,
            second_octet=second,
            third_octet=(user_id % 254) + 1,
        )
        for network in result["networks"].values():
            subnet = network["ipam"]["config"][0]["subnet"]
            assert subnet.startswith("10.1")
            assert not subnet.startswith("10.200.")


@pytest.mark.parametrize(
    "override",
    [
        {"image": "alpine:latest"},
        {"build": "."},
        {"privileged": True},
        {"network_mode": "host"},
        {"cap_add": ["SYS_ADMIN"]},
        {"volumes": ["/var/run/docker.sock:/var/run/docker.sock"]},
        {"devices": ["/dev/kvm"]},
        {"environment": {"OCR_GATEWAY": "10.0.0.1"}},
        {"labels": {"ocr_lab_net": "false", "ip_offset": "21"}},
        {"labels": {}},
    ],
)
def test_unsafe_service_is_rejected(override):
    compose = _compose()
    compose["services"]["h1"] = _node(**override)
    with pytest.raises(topology_engine.TopologyError):
        _expand(compose)


def test_unknown_node_and_duplicate_link_are_rejected():
    with pytest.raises(topology_engine.TopologyError):
        _expand(_compose(links=[{"from": "h1", "to": "missing"}]))

    with pytest.raises(topology_engine.TopologyError):
        _expand(
            _compose(
                links=[
                    {"from": "h1", "to": "r1"},
                    {"from": "r1", "to": "h1"},
                ]
            )
        )


def test_self_link_and_missing_password_are_rejected():
    with pytest.raises(topology_engine.TopologyError):
        _expand(_compose(links=[{"from": "h1", "to": "h1"}]))

    compose = _compose()
    compose["x-ocr-topology"]["training_password"] = ""
    with pytest.raises(topology_engine.TopologyError):
        _expand(compose)


def test_node_count_and_link_count_are_bounded():
    nodes = {
        f"n{index}": {"service": "h1", "role": "host"}
        for index in range(topology_engine.MAX_NODES + 1)
    }
    with pytest.raises(topology_engine.TopologyError):
        _expand(_compose(nodes=nodes))
