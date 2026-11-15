"""Static checks for the OpenWrt network-appliance lab."""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
LAB = REPO / "platform" / "labs" / "Network" / "network-12-6-appliance-segment"
WORKBOOK = REPO / "Workbook" / "CH_NET12_Device_Topology"
OPENWRT_DIGEST = (
    "openwrt/rootfs@sha256:"
    "46c12e45e9071aa5afb23ee0a1cda75e6a34f49eb0cf4f6fd171c6be2ce0162f"
)


def _lab() -> dict:
    return yaml.safe_load((LAB / "lab.yaml").read_text(encoding="utf-8"))


def _compose() -> dict:
    return yaml.safe_load((LAB / "docker-compose.yml").read_text(encoding="utf-8"))


def test_lab_and_flag_are_present():
    lab = _lab()
    flag = lab["flag"]
    assert flag.startswith("OCR{")
    assert flag in (LAB / "containers" / "protected" / "flag").read_text(
        encoding="utf-8"
    )


def test_appliance_is_a_pinned_dual_homed_image():
    compose = _compose()
    assert compose["x-ocr-reviewed-image"] == OPENWRT_DIGEST
    appliance = compose["services"]["appliance"]
    assert appliance["image"] == OPENWRT_DIGEST
    assert appliance["labels"]["ip_offset"] == "70"
    assert appliance["cap_add"] == ["NET_ADMIN"]
    assert appliance["sysctls"]["net.ipv4.ip_forward"] == "1"
    assert set(appliance["networks"]) == {"default", "control"}
    assert compose["networks"]["control"]["internal"] is True


def test_protected_service_stays_off_the_lab_network():
    compose = _compose()
    protected = compose["services"]["protected"]
    assert protected["labels"]["ocr_lab_net"] == "false"
    assert "ip_offset" not in protected["labels"]
    assert protected["networks"] == ["control"]
    assert protected["cap_add"] == ["NET_ADMIN"]
    assert (LAB / "containers" / "protected" / "Dockerfile").is_file()


def test_workbook_and_nav_are_wired():
    lab = _lab()
    page = WORKBOOK / "05_Network_Appliance_Segment.md"
    assert page.is_file()
    assert "05_Network_Appliance_Segment" in lab["workbook"]
    nav = (REPO / "mkdocs-netfor.yml").read_text(encoding="utf-8")
    assert "05_Network_Appliance_Segment.md" in nav
    steps = lab["test"]["steps"]
    assert any("OCR{" in step["expect"] for step in steps)
    assert "OCR{" in steps[-1]["expect"]
