"""Tests for resolving lab-authored placeholders in student-facing text."""
import pytest

from app.services.lab_text import render_lab_text, target_address_map


class _Session:
    def __init__(self, subnet):
        self.network_subnet = subnet


class _Lab:
    def __init__(self, nodes, topology=None):
        self.topology_nodes = topology if topology is not None else __import__("json").dumps(nodes)
        self.id = 1


NODES = [
    {"id": "target", "ip_offset": "10"},
    {"id": "portal", "ip_offset": "91"},
]


def test_target_placeholder_resolves_to_session_address():
    lab = _Lab(NODES)
    text = "Query `{target.target}` and open `{target.portal}`."

    assert render_lab_text(text, lab, _Session("10.100.3.0/24")) == (
        "Query `10.100.3.10` and open `10.100.3.91`."
    )


def test_subnet_placeholder_resolves():
    lab = _Lab(NODES)
    assert (
        render_lab_text("subnet {subnet}", lab, _Session("10.100.3.0/24"))
        == "subnet 10.100.3.0/24"
    )


def test_unknown_node_is_left_visible():
    """A typo must stay visible for review instead of becoming an empty string."""
    lab = _Lab(NODES)
    assert render_lab_text("{target.nope}", lab, _Session("10.100.3.0/24")) == "{target.nope}"


def test_without_session_placeholders_are_untouched():
    lab = _Lab(NODES)
    assert render_lab_text("{target.target}", lab, None) == "{target.target}"


def test_empty_text_is_returned_as_is():
    assert render_lab_text(None, _Lab(NODES), _Session("10.100.3.0/24")) is None
    assert render_lab_text("", _Lab(NODES), _Session("10.100.3.0/24")) == ""


def test_address_map_ignores_nodes_without_offset():
    lab = _Lab([{"id": "target"}, {"id": "portal", "ip_offset": "91"}])
    assert target_address_map(lab, _Session("10.100.3.0/24")) == {"portal": "10.100.3.91"}
