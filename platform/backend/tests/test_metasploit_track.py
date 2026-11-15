"""Static checks for the original Metasploit Operations track."""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
LAB_ROOT = REPO / "platform" / "labs" / "Metasploit"
WORKBOOK = REPO / "Workbook"


def _labs():
    return sorted(
        path
        for path in LAB_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )


def test_eight_labs_with_unique_flags_and_matching_profiles():
    labs = _labs()
    assert len(labs) == 8

    flags = {}
    for lab_dir in labs:
        lab = yaml.safe_load((lab_dir / "lab.yaml").read_text(encoding="utf-8"))
        compose = yaml.safe_load(
            (lab_dir / "docker-compose.yml").read_text(encoding="utf-8")
        )
        target = compose["services"]["target"]
        flag = lab["flag"]

        assert flag not in flags, f"duplicate flag {flag}"
        flags[flag] = lab_dir.name
        assert compose["x-ocr-requires-kvm"] is True
        assert compose["x-ocr-reviewed-image"] == "ocr-metasploitable2:latest"
        assert target["image"] == "ocr-metasploitable2:latest"
        assert target["labels"]["ip_offset"] == "10"
        assert target["environment"]["LAB_FLAG"] == flag
        assert target["environment"]["LAB_PROFILE"] in {
            "web",
            "ssh",
            "mysql",
            "pivot",
            "root",
        }
        assert "rangebox" in lab["tools"]
        assert lab["visibility"] == "public"
        assert lab["test"]["steps"], f"{lab_dir.name} has no test steps"


def test_workbooks_exist_for_every_lab():
    for lab_dir in _labs():
        lab = yaml.safe_load((lab_dir / "lab.yaml").read_text(encoding="utf-8"))
        relative = lab["workbook"].removeprefix("wiki/range/msfpt/").rstrip("/")
        assert (WORKBOOK / f"{relative}.md").is_file(), lab_dir.name
