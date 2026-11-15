"""Static checks for the live Linux memory acquisition lab."""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
LAB = REPO / "platform/labs/Forensics/forensics-3-1-live-linux-memory"
WORKBOOK = REPO / "Workbook/CH_FOR03_Live_Memory/01_Live_Linux_Memory.md"


def test_live_memory_lab_contract():
    lab = yaml.safe_load((LAB / "lab.yaml").read_text(encoding="utf-8"))
    compose = yaml.safe_load((LAB / "docker-compose.yml").read_text(encoding="utf-8"))
    target = compose["services"]["target"]

    assert compose["x-ocr-kvm-preferred"] is True
    assert compose["x-ocr-reviewed-image"] == "ocr-ubuntu-memory:latest"
    assert target["image"] == "ocr-ubuntu-memory:latest"
    assert target["environment"]["LAB_FLAG"] == lab["flag"]
    assert target["labels"]["ip_offset"] == "10"
    assert "rangebox" in lab["tools"]
    assert lab["credentials"][0]["username"] == "analyst"
    assert lab["test"]["steps"]
    assert WORKBOOK.is_file()
