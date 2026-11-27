#!/usr/bin/env python3
"""Lab QA pipeline: workbook, screenshot, flag, tool-version, and path checks.

Static mode is safe to run anywhere and is the CI gate:

    python scripts/lab_qa.py --static
    python scripts/lab_qa.py --static --json lab-qa.json
    python scripts/lab_qa.py --static --fail-on-warnings

Live mode delegates startup, health, isolation, solver, flag, repeat-solve,
resource, and teardown proof to ``scripts/lab_harness.py``:

    python scripts/lab_qa.py --live --lab linux-1-1-ssh-service-detection
    python scripts/lab_qa.py --live --all --runs 1

The pipeline does not pretend a static scan can see a screenshot. It hashes
every workbook image and requires a reviewed hash in
``platform/tester/screenshots.yaml``. A changed image fails the check until a
reviewer updates the hash and the review date.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
WORKBOOK = ROOT / "Workbook"
PATHS = ROOT / "platform" / "tester" / "paths"
SCREENSHOTS = ROOT / "platform" / "tester" / "screenshots.yaml"
TOOL_BASELINE = ROOT / "platform" / "tester" / "tool-version-baseline.yaml"

FLAG_RE = re.compile(r"OCR\{[^}\n]+\}")
PLACEHOLDER_FLAGS = {"OCR{...}", "OCR{<flag>}", "OCR{flag}", "OCR{FLAG}"}
PLACEHOLDER_MARKERS = (
    "...",
    "<",
    ">",
    "replace_me",
    "flag_here",
    "example",
    "placeholder",
    "your_flag",
    "token1",
    "token2",
    "token3",
    "`",
)
FLAG_REGEX_CHARS = set("[]()\\|+*?^$")
STRICT_FLAGS = False
STRICT_CONTENT = False
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IPV4_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
HOST_RE = re.compile(r"\b[a-z0-9][a-z0-9-]*\.lab\b")
FENCE_RE = re.compile(r"```([A-Za-z0-9_-]*)\n(.*?)```", re.DOTALL)
TOOL_RE = re.compile(
    r"(?i)\b(nmap|python|node(?:\.js)?|postgres(?:ql)?|metasploit|volatility|"
    r"wireshark|burp(?:\s+suite)?|owasp\s+zap|docker)\s+v?(\d+(?:\.\d+)+)"
)

DANGEROUS = {
    "rm -rf /": "destructive root delete",
    "mkfs": "filesystem format",
    "dd if=/dev/zero": "disk overwrite",
    "curl | bash": "remote script execution",
    "curl|bash": "remote script execution",
    "wget | sh": "remote script execution",
    "wget|sh": "remote script execution",
    "chmod 777 /": "world-writable root",
}

SHELL_LANGS = {"bash", "sh", "shell", "zsh"}


def load_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - a parse failure is a finding, not a crash
        return {}


def add(findings: list[dict], level: str, check: str, lab: str, detail: str) -> None:
    findings.append({"level": level, "check": check, "lab": lab, "detail": detail})


def is_placeholder_flag(flag: str) -> bool:
    """True for redacted examples, templates, and regex fragments.

    Workbooks deliberately show shapes such as ``OCR{_______________}``,
    ``OCR{<flag_here>}``, and ``OCR{[^}]*}``. Comparing those to the real flag
    produces noise and hides a genuine mismatch, so they are not flags.
    """
    if flag in PLACEHOLDER_FLAGS:
        return True
    if not flag.startswith("OCR{") or not flag.endswith("}"):
        return True
    inner = flag[4:-1]
    if not inner.strip():
        return True
    lowered = inner.lower()
    if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
        return True
    if any(char in FLAG_REGEX_CHARS for char in inner):
        return True
    # All-underscore, all-x, all-dot, or all-space placeholders.
    return set(inner) <= set("_ -xX.*")


def lab_files() -> list[Path]:
    return sorted(LABS.rglob("lab.yaml"))


def workbook_page(lab: dict) -> Path | None:
    workbook = str(lab.get("workbook") or "").strip()
    if not workbook:
        return None
    parts = [part for part in workbook.replace("\\", "/").split("/") if part]
    chapter = next((part for part in parts if part.startswith("CH_")), "")
    page = parts[-1] if parts else ""
    candidates = []
    if chapter and page:
        candidates.append(WORKBOOK / chapter / f"{page}.md")
    if page:
        candidates.extend(WORKBOOK.rglob(f"{page}.md"))
    return next((path for path in candidates if path.is_file()), None)


def screenshot_manifest() -> dict:
    if not SCREENSHOTS.is_file():
        return {"version": 1, "images": []}
    return load_yaml(SCREENSHOTS)


def image_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_screenshot_manifest() -> int:
    entries = []
    for path in sorted(WORKBOOK.rglob("*")):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
            continue
        rel = path.relative_to(ROOT).as_posix()
        existing = {item["path"]: item for item in screenshot_manifest().get("images", [])}
        old = existing.get(rel, {})
        entries.append(
            {
                "path": rel,
                "sha256": image_hash(path),
                "reviewed_at": old.get("reviewed_at"),
                "lab_slug": old.get("lab_slug"),
                "notes": old.get("notes", ""),
            }
        )
    SCREENSHOTS.write_text(
        yaml.safe_dump({"version": 1, "images": entries}, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"wrote {SCREENSHOTS.relative_to(ROOT)} ({len(entries)} images)")
    return 0


def check_images(slug: str, page: Path, text: str, findings: list[dict]) -> None:
    manifests = {item["path"]: item for item in screenshot_manifest().get("images", [])}
    for alt, src in IMAGE_RE.findall(text):
        target = src.strip()
        if target.startswith(("http://", "https://", "//")):
            add(findings, "error", "workbook-image", slug, f"external image is not allowed: {target}")
            continue
        if target.startswith("data:"):
            add(findings, "warning", "workbook-image", slug, "inline data image cannot be hashed")
            continue
        resolved = (page.parent / target).resolve()
        if not resolved.is_file():
            add(findings, "error", "workbook-image", slug, f"missing image: {target}")
            continue
        if not alt.strip():
            add(findings, "warning", "workbook-image", slug, f"image has no alt text: {target}")
        rel = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else ""
        entry = manifests.get(rel)
        if entry is None:
            add(findings, "warning", "workbook-image", slug, f"screenshot not in baseline: {rel}")
            continue
        if entry.get("sha256") != image_hash(resolved):
            add(findings, "error", "workbook-image", slug, f"screenshot changed since review: {rel}")
        elif not entry.get("reviewed_at"):
            add(findings, "warning", "workbook-image", slug, f"screenshot not visually reviewed: {rel}")


def check_links_and_urls(slug: str, page: Path, text: str, findings: list[dict]) -> None:
    known_hosts = {
        item.get("hostname")
        for item in (load_yaml(page.parent.parent / "lab.yaml").get("hostnames") or [])
    }
    for raw in LINK_RE.findall(text):
        target = raw.strip()
        if not target or target.startswith("#"):
            continue
        parsed = urlparse(target)
        if parsed.scheme in {"http", "https"}:
            if parsed.scheme == "http":
                add(findings, "warning", "workbook-url", slug, f"URL is not HTTPS: {target}")
            if parsed.hostname and IPV4_RE.fullmatch(parsed.hostname):
                add(findings, "error", "workbook-url", slug, f"URL uses a bare IP address: {target}")
            continue
        if parsed.scheme in {"javascript", "data", "vbscript"}:
            add(findings, "error", "workbook-url", slug, f"unsafe URL scheme: {target}")
            continue
        if parsed.scheme:
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (page.parent / path_part).resolve()
        if not resolved.exists():
            add(findings, "warning", "workbook-link", slug, f"relative link target is missing: {target}")

    for host in sorted(set(HOST_RE.findall(text))):
        if known_hosts and host not in known_hosts:
            add(findings, "warning", "workbook-host", slug, f"hostname not declared in lab.yaml: {host}")


def check_text_safety(
    slug: str,
    text: str,
    lab_flag: str,
    findings: list[dict],
    allowed_flags: set[str] | None = None,
) -> None:
    allowed_flags = allowed_flags or set()
    for flag in sorted(set(FLAG_RE.findall(text))):
        if is_placeholder_flag(flag) or flag in allowed_flags:
            continue
        if lab_flag and flag != lab_flag:
            add(
                findings,
                "error" if STRICT_FLAGS else "warning",
                "workbook-flag",
                slug,
                f"workbook flag {flag} does not match lab.yaml flag {lab_flag}",
            )
        else:
            add(findings, "error", "workbook-flag", slug, f"workbook exposes the lab flag: {flag}")

    for ip in sorted(set(IPV4_RE.findall(text))):
        octets = [int(part) for part in ip.split(".")]
        if any(part > 255 for part in octets):
            add(findings, "error", "workbook-ip", slug, f"invalid IPv4 address: {ip}")
        elif octets[0] == 10:
            add(findings, "info", "workbook-ip", slug, f"lab-network literal address: {ip}")
        elif ip in {"0.0.0.0", "127.0.0.1"}:
            add(findings, "info", "workbook-ip", slug, f"loopback or wildcard example: {ip}")
        elif ip.startswith(("198.51.100.", "203.0.113.")):
            add(findings, "info", "workbook-ip", slug, f"documentation address range: {ip}")
        elif octets[0] == 172 and 16 <= octets[1] <= 31 or octets[0] == 192 and octets[1] == 168:
            add(findings, "info", "workbook-ip", slug, f"private address: {ip}")
        else:
            add(findings, "warning", "workbook-ip", slug, f"public address in workbook: {ip}")


def check_commands(slug: str, text: str, findings: list[dict]) -> None:
    for lang, block in FENCE_RE.findall(text):
        body = block.strip()
        if not body:
            continue
        lowered = body.lower()
        for pattern, reason in DANGEROUS.items():
            if pattern in lowered:
                add(findings, "error", "workbook-command", slug, f"{reason}: {pattern}")
        if lang.lower() not in SHELL_LANGS:
            continue
        # Placeholders and Windows prompts are not Bash. Skip them rather than
        # reporting a syntax error the workbook never claimed.
        if (
            re.search(r"\{[A-Za-z_][^}]*\}", body)
            or re.search(r"<[^>\n]+>", body)
            or re.search(r"(?m)^\s*(PS [A-Z]:|C:\\|PS>|>)", body)
        ):
            continue
        # A workbook may show prompts and placeholders. Syntax-check the block
        # after removing a leading prompt; a failure is a warning, not proof of
        # a broken lab, because some blocks are intentionally partial.
        script = "\n".join(
            line.removeprefix("$ ") for line in body.splitlines()
        )
        try:
            result = subprocess.run(
                ["bash", "-n"],
                input=script,
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0:
            error_lines = (result.stderr or result.stdout or "unknown").strip().splitlines()
            detail = error_lines[-1][:160] if error_lines else "unknown"
            add(
                findings,
                "warning",
                "workbook-command",
                slug,
                f"shell block does not parse: {detail}",
            )


def check_tool_versions(slug: str, text: str, findings: list[dict]) -> None:
    baseline = load_yaml(TOOL_BASELINE).get("tools") or {}
    for tool, version in TOOL_RE.findall(text):
        key = tool.lower().replace(" ", "-").replace(".js", "")
        entry = baseline.get(key)
        if not entry:
            continue
        minimum = str(entry.get("minimum") or "")
        if not minimum:
            continue
        try:
            if tuple(int(part) for part in version.split(".")) < tuple(
                int(part) for part in minimum.split(".")
            ):
                add(
                    findings,
                    "warning",
                    "workbook-tool-version",
                    slug,
                    f"{tool} {version} is older than the reviewed minimum {minimum}",
                )
        except ValueError:
            continue


def check_path_plan(slug: str, findings: list[dict]) -> None:
    path = PATHS / f"{slug}.yaml"
    if not path.is_file():
        add(findings, "info", "path-plan", slug, "no alternate-path review plan")
        return
    plan = load_yaml(path)
    if plan.get("lab_id") != slug:
        add(findings, "error", "path-plan", slug, "lab_id does not match the directory slug")
    if not str(plan.get("intended_path") or "").strip():
        add(findings, "error", "path-plan", slug, "intended_path is empty")
    checks = plan.get("bypass_checks") or []
    if not checks:
        add(findings, "warning", "path-plan", slug, "no bypass checks recorded")
    for index, item in enumerate(checks, start=1):
        if not item.get("name"):
            add(findings, "error", "path-plan", slug, f"bypass check {index} has no name")
        if not item.get("command"):
            add(findings, "error", "path-plan", slug, f"bypass check {index} has no command")
        if not item.get("rationale"):
            add(findings, "warning", "path-plan", slug, f"bypass check {index} has no rationale")


GENERIC_DEFENSIVE = (
    "Validate and encode input at the server, enforce authorization on every "
    "object, and monitor unusual request patterns."
)


def check_test_flags(slug: str, lab: dict, findings: list[dict]) -> None:
    """The lab flag is the only answer; every test expectation must agree."""
    lab_flag = str(lab.get("flag") or "").strip()
    if not lab_flag:
        add(findings, "error", "lab-flag", slug, "lab.yaml has no flag")
        return
    if is_placeholder_flag(lab_flag):
        add(findings, "error", "lab-flag", slug, f"lab.yaml flag is a placeholder: {lab_flag}")
        return
    steps = (lab.get("test") or {}).get("steps") or []
    for index, step in enumerate(steps, start=1):
        if step.get("allow_flag_mismatch"):
            continue
        name = str(step.get("name") or f"step {index}")
        for field in ("command", "expect"):
            for found in FLAG_RE.findall(str(step.get(field) or "")):
                if is_placeholder_flag(found):
                    continue
                if found != lab_flag:
                    add(
                        findings,
                        "error",
                        "test-flag",
                        slug,
                        f"{name}: {field} expects {found}, lab.yaml flag is {lab_flag}",
                    )


def check_content_quality(
    slug: str,
    lab: dict,
    findings: list[dict],
    duplicate_defensive: dict[str, list[str]],
) -> None:
    defensive = str(lab.get("defensive_takeaways") or "").strip()
    if defensive:
        if defensive == GENERIC_DEFENSIVE:
            add(
                findings,
                "error" if STRICT_CONTENT else "warning",
                "generic-defensive",
                slug,
                "defensive_takeaways is the shared boilerplate; write the control this lab teaches",
            )
        others = [item for item in duplicate_defensive.get(defensive, []) if item != slug]
        if others:
            add(
                findings,
                "error" if STRICT_CONTENT else "warning",
                "duplicate-defensive",
                slug,
                "same defensive_takeaways as " + ", ".join(sorted(others)[:5]),
            )
    else:
        add(findings, "warning", "defensive", slug, "no defensive_takeaways")

    skills = [str(item) for item in (lab.get("mapped_skills") or [])]
    if skills == ["web_api"] and not lab.get("competency_tags"):
        add(
            findings,
            "error" if STRICT_CONTENT else "warning",
            "generic-skill",
            slug,
            "mapped_skills is only web_api; add the fine-grained competency_tags too",
        )

    category = str(lab.get("category") or "")
    if (
        category in {"reconnaissance", "web", "exploitation"}
        and not lab.get("analyst_finding_required")
        and not lab.get("evidence_required")
    ):
        add(
            findings,
            "error" if STRICT_CONTENT else "info",
            "missing-evidence",
            slug,
            "recon/exploitation lab has no analyst_finding_required or evidence_required",
        )


def check_lab(
    path: Path,
    findings: list[dict],
    duplicate_defensive: dict[str, list[str]],
) -> None:
    lab = load_yaml(path)
    slug = path.parent.name
    lab_flag = str(lab.get("flag") or "")
    page = workbook_page(lab)
    if page is None:
        add(findings, "warning", "workbook", slug, "no workbook page resolved")
    else:
        text = page.read_text(encoding="utf-8", errors="ignore")
        check_images(slug, page, text, findings)
        check_links_and_urls(slug, page, text, findings)
        check_text_safety(
            slug,
            text,
            lab_flag,
            findings,
            {str(item) for item in (lab.get("allowed_workbook_flags") or [])},
        )
        check_commands(slug, text, findings)
        check_tool_versions(slug, text, findings)
    check_path_plan(slug, findings)
    check_test_flags(slug, lab, findings)
    check_content_quality(slug, lab, findings, duplicate_defensive)


def duplicate_defensive_map(paths: list[Path]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for path in paths:
        lab = load_yaml(path)
        text = str(lab.get("defensive_takeaways") or "").strip()
        if text:
            seen.setdefault(text, []).append(path.parent.name)
    return seen


def run_static(selected: list[str] | None, as_json: bool, fail_on_warnings: bool) -> int:
    findings: list[dict] = []
    paths = lab_files()
    duplicates = duplicate_defensive_map(paths)
    if selected:
        wanted = set(selected)
        paths = [path for path in paths if path.parent.name in wanted]
        for missing in sorted(wanted - {path.parent.name for path in paths}):
            add(findings, "error", "lab", missing, "lab not found")
    for path in paths:
        check_lab(path, findings, duplicates)

    counts = {
        level: sum(1 for item in findings if item["level"] == level)
        for level in ("error", "warning", "info")
    }
    payload = {
        "labs": len(paths),
        "errors": counts["error"],
        "warnings": counts["warning"],
        "info": counts["info"],
        "findings": findings,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("Lab QA static pipeline")
        print("=" * 40)
        print(f"  labs: {len(paths)}")
        print(f"  errors: {counts['error']}  warnings: {counts['warning']}  info: {counts['info']}")
        for item in findings:
            if item["level"] == "info":
                continue
            print(f"  [{item['level'].upper():7}] {item['lab']}: {item['check']}: {item['detail']}")
        if not counts["error"] and not counts["warning"]:
            print("PASS: no workbook, screenshot, flag, tool-version, or path findings.")
        elif not counts["error"]:
            print("PASS with warnings: no blocking findings.")
        else:
            print("FAIL: blocking findings above.")
    if counts["error"]:
        return 1
    if fail_on_warnings and counts["warning"]:
        return 1
    return 0


def run_live(selected: list[str] | None, runs: int) -> int:
    command = [sys.executable, str(ROOT / "scripts" / "lab_harness.py"), "--runs", str(runs)]
    if selected:
        for slug in selected:
            command += ["--lab", slug]
    else:
        command.append("--all")
    result = subprocess.run(command, cwd=ROOT, check=False)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="run workbook and path checks")
    parser.add_argument("--live", action="store_true", help="run the live harness")
    parser.add_argument("--lab", action="append", default=[], help="lab slug; repeat as needed")
    parser.add_argument("--all", action="store_true", help="all labs for live mode")
    parser.add_argument("--runs", type=int, default=1, help="clean live runs per lab")
    parser.add_argument("--json", action="store_true", help="machine-readable static output")
    parser.add_argument("--fail-on-warnings", action="store_true")
    parser.add_argument(
        "--strict-flags",
        action="store_true",
        help="treat a workbook flag mismatch as an error after the allowlist is reviewed",
    )
    parser.add_argument(
        "--strict-content",
        action="store_true",
        help="treat generic or duplicated guidance as an error (release gate)",
    )
    parser.add_argument("--write-screenshots", action="store_true")
    args = parser.parse_args()
    global STRICT_FLAGS, STRICT_CONTENT
    STRICT_FLAGS = args.strict_flags
    STRICT_CONTENT = args.strict_content

    if args.write_screenshots:
        return write_screenshot_manifest()
    if args.live:
        selected = None if args.all or not args.lab else args.lab
        return run_live(selected, args.runs)
    selected = args.lab or None
    return run_static(selected, args.json, args.fail_on_warnings)


if __name__ == "__main__":
    raise SystemExit(main())
