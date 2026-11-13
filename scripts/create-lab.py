#!/usr/bin/env python3
"""Create a routed network-topology lab from a small node/link specification.

This is the lab-creation engine for the device topology feature. It writes a
validated `lab.yaml`, a Compose file using `x-ocr-topology`, a README, and a
workbook scaffold. The topology engine does the runtime work; this script makes
the authoring path one command.

Examples:
    python3 scripts/create-lab.py --track network --level 13 \
      --name "BGP Route Leak" \
      --node h1:host --node r1:router --node r2:router \
      --node svc:service:flag --link h1-r1 --link r1-r2 --link r2-svc \
      --pace guided --flag 'OCR{bgp_route_leak}'

    python3 scripts/create-lab.py --list-tracks

    python3 scripts/create-lab.py --track forensics --level 2 \
      --name "Evidence Path" --node w1:host --node r1:router \
      --node case:service:flag --link w1-r1 --link r1-case \
      --pace independent --dry-run
"""
from __future__ import annotations

import argparse
import re
import secrets
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "platform" / "labs"
VALIDATOR = ROOT / "scripts" / "validate-lab.py"

TRACK_DIRS = {
    "windows": "Windows",
    "linux": "Linux",
    "web": "Web",
    "network": "Network",
    "malware": "Malware",
    "osint": "OSINT",
    "high-school": "High School",
    "software-security": "Software Security",
    "identity": "Identity",
    "forensics": "Forensics",
    "ot": "OT",
    "ai": "AI",
}
ROLES = {"host", "router", "service"}
SLUG_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*-(?:\d+-\d+|midterm-\d+|final-\d+)-[a-z0-9-]+$")


def slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", text)


def parse_node(raw: str) -> dict:
    parts = raw.split(":")
    if len(parts) < 2:
        raise SystemExit(f"node '{raw}' must look like id:host|router|service[:flag]")
    node_id, role = parts[0].strip().lower(), parts[1].strip().lower()
    if not re.match(r"^[a-z][a-z0-9_-]{1,31}$", node_id):
        raise SystemExit(f"invalid node id '{node_id}'")
    if role not in ROLES:
        raise SystemExit(f"node '{node_id}' role must be one of {sorted(ROLES)}")
    return {"id": node_id, "role": role, "flag": len(parts) > 2 and parts[2].strip() == "flag"}


def parse_link(raw: str) -> tuple[str, str]:
    if "-" not in raw:
        raise SystemExit(f"link '{raw}' must look like from-to")
    left, right = (part.strip().lower() for part in raw.split("-", 1))
    if not left or not right or left == right:
        raise SystemExit(f"invalid link '{raw}'")
    return left, right


def build_spec(args, flag: str) -> dict:
    nodes = [parse_node(raw) for raw in (args.node or [])]
    if not nodes:
        nodes = [
            {"id": "h1", "role": "host", "flag": False},
            {"id": "r1", "role": "router", "flag": False},
            {"id": "svc", "role": "service", "flag": True},
        ]
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        raise SystemExit("node ids must be unique")
    if not any(node["role"] == "service" for node in nodes):
        raise SystemExit("a topology needs at least one service node")

    links = [parse_link(raw) for raw in (args.link or [])]
    if not links:
        links = [(nodes[index]["id"], nodes[index + 1]["id"]) for index in range(len(nodes) - 1)]
    for left, right in links:
        if left not in ids or right not in ids:
            raise SystemExit(f"link {left}-{right} references an unknown node")
        if left == right:
            raise SystemExit(f"link {left}-{right} connects a node to itself")

    for offset, node in enumerate(nodes, start=21):
        node["ip_offset"] = str(offset)
    services = [node for node in nodes if node["role"] == "service"]
    flagged = next((node for node in services if node["flag"]), None)
    if flagged is None:
        flagged = services[0]
        flagged["flag"] = True
    for node in nodes:
        node["flag"] = node is flagged

    return {"nodes": nodes, "links": links, "flagged": flagged, "flag": flag}


def node_type(role: str) -> str:
    return {"host": "workstation", "router": "router", "service": "server"}[role]


def node_limits(role: str) -> dict:
    if role == "router":
        return {"mem_limit": "256m", "cpus": 0.25, "pids_limit": 96}
    return {"mem_limit": "192m", "cpus": 0.20, "pids_limit": 96}


def compose_doc(spec: dict, password: str) -> dict:
    nodes = {}
    for node in spec["nodes"]:
        nodes[node["id"]] = {"service": node["id"], "role": node["role"]}
    spec_block = {
        "training_user": "analyst",
        "training_password": password,
        "nodes": nodes,
        "links": [{"from": left, "to": right} for left, right in spec["links"]],
    }
    spec_block["nodes"][spec["flagged"]["id"]].update(
        {"flag": spec["flag"], "http_port": 80}
    )

    services = {}
    for node in spec["nodes"]:
        service = {
            "image": "ocr-lab/topology-node:latest",
            "hostname": node["id"],
            "labels": {"ip_offset": node["ip_offset"]},
            "cap_add": ["NET_ADMIN"],
            "security_opt": ["no-new-privileges:true"],
            **node_limits(node["role"]),
            "restart": "unless-stopped",
        }
        if node["flag"]:
            service["environment"] = {"FLAG": spec["flag"]}
        services[node["id"]] = service
    return {"x-ocr-topology": spec_block, "services": services}


def test_steps(spec: dict, pace: str) -> list[dict]:
    host = next((node for node in spec["nodes"] if node["role"] == "host"), spec["nodes"][0])
    router = next((node for node in spec["nodes"] if node["role"] == "router"), None)
    service = spec["flagged"]
    steps = [
        {
            "name": f"SSH to {host['id']}",
            "command": (
                f"sshpass -p '{{cred.analyst.pass}}' ssh -o StrictHostKeyChecking=no "
                f"-o UserKnownHostsFile=/dev/null {{cred.analyst.user}}@{{target.{host['id']}}} "
                "'echo connected' 2>&1"
            ),
            "expect": "connected",
            "timeout": 20,
        }
    ]
    if router is not None:
        steps.extend(
            [
                {
                    "name": f"{router['id']} reports its role",
                    "command": f"curl -s --connect-timeout 5 http://{{target.{router['id']}}}:8080/status",
                    "expect": '"role": "router"',
                    "timeout": 15,
                },
                {
                    "name": f"{host['id']} uses the router",
                    "command": (
                        f"sshpass -p '{{cred.analyst.pass}}' ssh -o StrictHostKeyChecking=no "
                        f"-o UserKnownHostsFile=/dev/null {{cred.analyst.user}}@{{target.{host['id']}}} "
                        "'ip route | grep default' 2>&1"
                    ),
                    "expect": "default via",
                    "timeout": 20,
                },
                {
                    "name": f"{router['id']} forwards IPv4",
                    "command": (
                        f"sshpass -p '{{cred.analyst.pass}}' ssh -o StrictHostKeyChecking=no "
                        f"-o UserKnownHostsFile=/dev/null {{cred.analyst.user}}@{{target.{router['id']}}} "
                        "'cat /proc/sys/net/ipv4/ip_forward' 2>&1"
                    ),
                    "expect": "1",
                    "timeout": 20,
                },
                {
                    "name": "Retrieve the flag through the router",
                    "command": (
                        f"IP=$(curl -s --connect-timeout 5 http://{{target.{router['id']}}}:8080/status "
                        f"| jq -r '.links[] | select(.peer==\"{service['id']}\") | .peer_ip'); "
                        f"sshpass -p '{{cred.analyst.pass}}' ssh -o StrictHostKeyChecking=no "
                        f"-o UserKnownHostsFile=/dev/null {{cred.analyst.user}}@{{target.{host['id']}}} "
                        f"\"wget -qO- http://$IP/flag\" 2>&1"
                    ),
                    "expect": spec["flag"],
                    "timeout": 30,
                },
            ]
        )
    else:
        steps.append(
            {
                "name": "Retrieve the flag",
                "command": f"curl -s --connect-timeout 5 http://{{target.{service['id']}}}/flag",
                "expect": spec["flag"],
                "timeout": 15,
            }
        )
    return steps


def lab_doc(args, spec: dict, slug: str, password: str) -> dict:
    guided = args.pace == "guided"
    hints = []
    if guided:
        hints = [
            {"text": "Start with the router status endpoint. It lists every peer, link address, and /29 subnet."},
            {"text": "On the host, `ip route` shows the default next hop. On the router, confirm `ip_forward=1`."},
            {"text": "Use the service's link address, not its management address, for the final request."},
            {"text": "Record each hop, interface, peer, and subnet so another analyst can reproduce the path."},
        ]
    else:
        hints = [
            {"text": "Map every link before choosing a service. Verify the service identity, then prove the path with link addresses."}
        ]
    categories = ["general", "network", "forensics", "web", "linux", "windows"]
    topology_nodes = []
    for index, node in enumerate(spec["nodes"], start=1):
        topology_nodes.append(
            {
                "id": node["id"],
                "label": node["id"],
                "type": node_type(node["role"]),
                "ip_offset": node["ip_offset"],
                "ports": [22, 8080] + ([80] if node["flag"] else []),
                "services": ["OpenSSH", "Status"] + (["HTTP flag"] if node["flag"] else []),
                "x": index,
                "y": 2,
            }
        )
    doc = {
        "title": args.name,
        "category": args.category,
        "difficulty": args.difficulty,
        "estimated_time": args.duration,
        "prerequisites": list(args.prereq or []),
        "learning_outcomes": [
            "Map the topology from the node status endpoint",
            "Distinguish management addresses from per-link addresses",
            "Explain the host default route and router forwarding",
            "Reach the protected service through the routed path",
            "Record the path so another analyst can reproduce it",
        ],
        "mapped_skills": ["incident_forensics", "network_systems"]
        if args.track == "forensics"
        else ["network_systems"],
        "assessment_criteria": [
            "Submit the correct flag.",
            "Pass every automated test step in the lab manifest.",
        ],
        "mitre_attack": [
            {
                "tactic": "Discovery",
                "technique": "T1016",
                "technique_name": "System Network Configuration Discovery",
                "detection": "Alert on unexpected topology and route discovery from a learner workstation.",
            }
        ],
        "owner": "OpenCyberRange Curriculum",
        "content_version": "4.0",
        "reviewed_at": date.today().isoformat(),
        "review_status": "generated scaffold; live walkthrough pending",
        "description": args.description or f"{args.name}: a routed topology exercise.",
        "scenario": (
            "A host reaches a protected service through a router. Map the links, "
            "confirm the host route and router forwarding, then recover the flag "
            "through the routed path."
        ),
        "credentials": [
            {
                "role": "analyst",
                "username": "analyst",
                "password": password,
                "description": "SSH access to each topology node",
            }
        ],
        "hints": hints,
        "flag": spec["flag"],
        "visibility": args.visibility,
        "week": args.level,
        "troubleshooting": "If a node is unreachable, confirm the lab is running and use the management IP. If the status endpoint fails, rebuild ocr-lab/topology-node:latest.",
        "defensive_takeaways": "A routed segment is a control and monitoring point. Document the path and verify both directions.",
        "difficulty_evidence": "Generated scaffold; engine unit tests apply.",
        "difficulty_evidence_source": "generated_scaffold",
        "difficulty_evidence_sample": 1,
        "difficulty_evidence_quality": "provisional",
        "difficulty_evidence_reviewed_at": date.today().isoformat(),
        "workbook": f"wiki/range/{args.track}/{slug}/00_Introduction/",
        "topology": {
            "nodes": topology_nodes,
            "edges": [
                {"from": left, "to": right, "label": "point-to-point /29", "access": "routed"}
                for left, right in spec["links"]
            ],
        },
        "test": {"steps": test_steps(spec, args.pace)},
    }
    if doc["category"] not in categories:
        doc["category"] = "network"
    return doc


def workbook_doc(args, spec: dict, slug: str) -> str:
    lines = [
        f"# {args.name}",
        "",
        "## Scenario",
        "",
        "A host reaches a protected service through a router. Reconstruct the path",
        "from the node status endpoints and recover the flag through the routed link.",
        "",
        "## Topology",
        "",
        "| Node | Role | Link peers |",
        "|---|---|---|",
    ]
    peers = {node["id"]: [] for node in spec["nodes"]}
    for left, right in spec["links"]:
        peers[left].append(right)
        peers[right].append(left)
    for node in spec["nodes"]:
        lines.append(f"| `{node['id']}` | {node['role']} | {', '.join(peers[node['id']]) or '-'} |")
    lines.extend(
        [
            "",
            "## Steps",
            "",
            "1. Read `http://<router-management-ip>:8080/status`.",
            "2. On the host, run `ip route` and record the default next hop.",
            "3. On the router, confirm `cat /proc/sys/net/ipv4/ip_forward` returns `1`.",
            "4. Use the service **link** address from the status document to request `/flag`.",
            "5. Record each hop, interface, peer, and subnet.",
            "",
            "## Notes",
            "",
            f"Generated by `scripts/create-lab.py` for `{slug}`. Add this page to the",
            "appropriate MkDocs navigation before publishing.",
            "",
        ]
    )
    return "\n".join(lines)


def readme_doc(args, spec: dict, slug: str) -> str:
    lines = [
        f"# {args.name}",
        "",
        f"Generated topology lab `{slug}`.",
        "",
        "## Nodes",
        "",
        "| Node | Role | IP offset | Flag |",
        "|---|---|---|---|",
    ]
    for node in spec["nodes"]:
        lines.append(
            f"| `{node['id']}` | {node['role']} | {node['ip_offset']} | {'yes' if node['flag'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Next steps",
            "",
            "1. Replace the scaffold flag and scenario text in `lab.yaml`.",
            "2. Add the workbook page to the track navigation.",
            "3. Run `python scripts/validate-lab.py <this directory>`.",
            "4. Build the node image: `docker build -t ocr-lab/topology-node:latest platform/topology-node`.",
            "5. Discover the lab: `python /app/app/scripts/discover_labs.py` in the backend container.",
            "6. Spawn it and complete it once before publishing.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--track", default="network", help="Track slug (default: network)")
    parser.add_argument("--level", type=int, default=13, help="Level number (default: 13)")
    parser.add_argument("--name", required=True, help="Human-readable lab name")
    parser.add_argument("--description", default=None)
    parser.add_argument("--lab-num", type=int, default=None)
    parser.add_argument("--difficulty", default="intermediate", choices=["beginner", "intermediate", "advanced", "expert"])
    parser.add_argument("--category", default="network")
    parser.add_argument("--duration", type=int, default=45)
    parser.add_argument("--visibility", default="draft", choices=["draft", "course", "public"])
    parser.add_argument("--node", action="append", help="id:host|router|service[:flag] (repeatable)")
    parser.add_argument("--link", action="append", help="from-to (repeatable)")
    parser.add_argument("--pace", default="guided", choices=["guided", "independent"])
    parser.add_argument("--prereq", action="append", help="Prerequisite lab slug (repeatable)")
    parser.add_argument("--flag", default=None)
    parser.add_argument("--training-password", default="Topology2026")
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list-tracks", action="store_true")
    args = parser.parse_args()

    if args.list_tracks:
        print("Tracks: " + ", ".join(sorted(TRACK_DIRS)))
        return 0
    if args.track not in TRACK_DIRS:
        parser.error(f"unknown track '{args.track}'; choose from {', '.join(sorted(TRACK_DIRS))}")
    if len(args.training_password) < 10:
        parser.error("--training-password must be at least 10 characters")

    flag = args.flag or f"OCR{{topology_{secrets.token_hex(4)}}}"
    spec = build_spec(args, flag)
    name_slug = slugify(args.name)
    track_dir = LABS / TRACK_DIRS[args.track]
    track_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(
        int(match.group(1))
        for path in track_dir.iterdir()
        if path.is_dir()
        for match in [re.match(rf"^{re.escape(args.track)}-{args.level}-(\d+)-", path.name)]
        if match
    )
    lab_num = args.lab_num or (max(existing, default=0) + 1)
    slug = f"{args.track}-{args.level}-{lab_num}-{name_slug}"
    if not SLUG_RE.match(slug):
        parser.error(f"generated slug '{slug}' does not match the validator pattern")
    lab_dir = track_dir / slug
    if lab_dir.exists():
        parser.error(f"directory already exists: {lab_dir}")

    compose = compose_doc(spec, args.training_password)
    lab = lab_doc(args, spec, slug, args.training_password)
    lab_text = yaml.safe_dump(lab, sort_keys=False, allow_unicode=True)
    lab_text = lab_text.replace(
        "learning_outcomes:",
        "# By completion students will be able to:\nlearning_outcomes:",
        1,
    )
    files = {
        lab_dir / "lab.yaml": lab_text,
        lab_dir / "docker-compose.yml": yaml.safe_dump(compose, sort_keys=False, allow_unicode=True),
        lab_dir / "README.md": readme_doc(args, spec, slug),
        ROOT / "Workbook" / slug / "00_Introduction.md": workbook_doc(args, spec, slug),
    }

    print(f"Track:    {args.track}")
    print(f"Level:    {args.level}")
    print(f"Lab:      {args.name}")
    print(f"Slug:     {slug}")
    print(f"Pace:     {args.pace}")
    print(f"Flag:     {flag}")
    print(f"Workbook: Workbook/{slug}/00_Introduction.md")
    print()

    if args.dry_run:
        for path in files:
            print(f"would create {path.relative_to(ROOT)}")
        return 0
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"created {path.relative_to(ROOT)}")

    if not args.no_validate:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(lab_dir)],
            cwd=ROOT,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print("validator reported problems; fix them before publishing", file=sys.stderr)
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
