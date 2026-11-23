"""Manifest and harness contract tests (no Docker required)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = _load("generate_lab_manifests", "generate-lab-manifests.py")
harness = _load("lab_harness", "lab_harness.py")


def test_expected_services_parses_ports_without_head_or_shell_flags():
    steps = [
        {"command": "nc -z -w 5 {target.target} 22 && echo 'port_open'"},
        {"command": "nc -w 5 {target.target} 22 </dev/null | head -1"},
        {"command": "nmap -Pn -n -p 22,80 -sV {target.target} 2>&1"},
        {"command": "curl -s http://{target.web}:8080/flag"},
    ]

    services = generator._expected_services(steps)

    assert services == [
        {"port": 22, "protocol": "tcp"},
        {"port": 80, "protocol": "tcp"},
        {"port": 8080, "protocol": "tcp"},
    ]


def test_memory_parser_handles_compose_units():
    assert generator._parse_memory_mb("512M") == 512
    assert generator._parse_memory_mb("1G") == 1024
    assert generator._parse_memory_mb("256MiB") == 256
    assert generator._parse_memory_mb(None) is None


def test_resolve_command_substitutes_target_credential_and_flag():
    resolved, problems = harness.resolve_command(
        "sshpass -p '{cred.analyst.pass}' ssh {cred.analyst.user}@{target.analyst} cat {flag}",
        {"analyst": "10.10.10.5"},
        {"analyst": {"user": "analyst", "pass": "Secret#1"}},
        "OCR{test}",
    )

    assert problems == []
    assert resolved == "sshpass -p 'Secret#1' ssh analyst@10.10.10.5 cat OCR{test}"


def test_resolve_command_reports_unknown_placeholders():
    resolved, problems = harness.resolve_command(
        "nc {target.missing} 22", {}, {}, ""
    )

    assert "{target.missing}" in resolved
    assert problems


def test_manifest_validation_rejects_missing_keys(tmp_path):
    errors = harness.validate_manifest({}, tmp_path / "bad.yaml")
    assert errors
    assert "missing keys" in errors[0]


def test_generated_manifest_contract_smoke():
    manifest = harness.load_manifest(
        ROOT / "platform/tester/manifests/linux-1-1-ssh-service-detection.yaml"
    )

    assert manifest["expected_flag"] == "{flag}"
    assert manifest["expected_flag_count"] == 1
    assert {"port": 22, "protocol": "tcp"} in manifest["expected_services"]
    assert manifest["solver"]["steps"]
    assert "control-plane" in manifest["forbidden_networks"]
    assert manifest["max_memory_mb"] > 0
    assert manifest["max_cpu"] > 0
