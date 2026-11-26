"""RangeBox proxy-network allocation across overlapping lab sessions."""

from __future__ import annotations

from types import SimpleNamespace

import docker
import pytest

from app.services.docker_manager import DockerManager, proxy_peer_ips


class _FakeNetwork:
    def __init__(self, name: str, subnet: str | None = None, containers=None):
        self.attrs = {
            "IPAM": {"Config": [{"Subnet": subnet}]} if subnet else {"Config": []},
            "Containers": containers or {},
        }
        self.name = name
        self.removed = False
        self.connected: list[str | None] = []

    def remove(self):
        self.removed = True

    def disconnect(self, container, force=False):
        return None

    def connect(self, container, ipv4_address=None):
        self.connected.append(ipv4_address)


class _FakeBackend:
    def __init__(self):
        self.attrs = {"NetworkSettings": {"Networks": {}}}


class _FakeContainers:
    def __init__(self, backend):
        self.backend = backend

    def get(self, name):
        return self.backend


class _FakeNetworks:
    def __init__(self, existing=None, blocked=None):
        self.existing = existing or {}
        self.blocked = blocked or set()
        self.created = []

    def get(self, name):
        if name in self.existing:
            return self.existing[name]
        raise docker.errors.NotFound(name)

    def list(self):
        return list(self.existing.values())

    def create(self, name, **kwargs):
        subnet = kwargs["ipam"]["Config"][0]["Subnet"]
        if subnet in self.blocked:
            raise Exception(
                "403 Client Error for http://docker-socket-proxy:2375/v1.57/networks/create: "
                'Forbidden ("invalid pool request: Pool overlaps with other one on this address space")'
            )
        self.created.append(subnet)
        return _FakeNetwork(name, subnet)


def _manager(networks):
    return SimpleNamespace(client=SimpleNamespace(networks=networks))


def test_proxy_peers_follow_the_network_address():
    assert proxy_peer_ips("10.200.212.0/29") == ("10.200.212.2", "10.200.212.3")
    assert proxy_peer_ips("10.200.212.8/29") == ("10.200.212.10", "10.200.212.11")


def test_allocator_moves_past_a_block_held_by_the_previous_lab():
    networks = _FakeNetworks(blocked={"10.200.212.0/29"})

    net, subnet = DockerManager._ensure_proxy_network(
        _manager(networks), "ocr-proxy-212-lab-b", 212, 212
    )

    assert subnet == "10.200.212.8/29"
    assert networks.created == ["10.200.212.8/29"]
    assert net.attrs["IPAM"]["Config"][0]["Subnet"] == subnet


def test_existing_network_is_reused_without_creating_another():
    name = "ocr-proxy-212-lab-a"
    networks = _FakeNetworks(existing={name: _FakeNetwork(name, "10.200.212.8/29")})

    net, subnet = DockerManager._ensure_proxy_network(_manager(networks), name, 212, 212)

    assert subnet == "10.200.212.8/29"
    assert networks.created == []
    assert net.name == name


def test_get_rangebox_ip_reads_the_allocated_subnet():
    name = "ocr-proxy-212-lab-a"
    networks = _FakeNetworks(existing={name: _FakeNetwork(name, "10.200.212.8/29")})

    assert DockerManager.get_rangebox_ip(_manager(networks), 212, "lab-a") == "10.200.212.10"


def test_allocator_fails_when_every_block_is_taken():
    networks = _FakeNetworks(
        blocked={f"10.200.212.{offset}/29" for offset in range(0, 256, 8)}
    )

    with pytest.raises(RuntimeError):
        DockerManager._ensure_proxy_network(
            _manager(networks), "ocr-proxy-212-lab", 212, 212
        )


def test_reattach_uses_the_addresses_of_the_allocated_block():
    name = "ocr-proxy-212-lab-b"
    proxy_net = _FakeNetwork(name, "10.200.212.8/29", containers={"abc": {}})
    networks = _FakeNetworks(existing={name: proxy_net})
    manager = SimpleNamespace(
        client=SimpleNamespace(
            networks=networks,
            containers=_FakeContainers(_FakeBackend()),
        )
    )

    assert DockerManager.ensure_proxy_attachments(manager) == [name]
    assert proxy_net.connected == ["10.200.212.11"]


def test_reattach_leaves_an_already_attached_network_alone():
    name = "ocr-proxy-212-lab-b"
    proxy_net = _FakeNetwork(name, "10.200.212.8/29", containers={"abc": {}})
    networks = _FakeNetworks(existing={name: proxy_net})
    backend = _FakeBackend()
    backend.attrs["NetworkSettings"]["Networks"] = {name: {}}
    manager = SimpleNamespace(
        client=SimpleNamespace(
            networks=networks,
            containers=_FakeContainers(backend),
        )
    )

    assert DockerManager.ensure_proxy_attachments(manager) == []
    assert proxy_net.connected == []
