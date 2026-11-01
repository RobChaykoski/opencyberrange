#!/usr/bin/env python3
"""Scaffold a new OpenCyberRange lab.

Creates a lab directory that already satisfies the validator: a lab.yaml with
the required fields, a docker-compose.yml with an ip_offset-labelled target, a
target Dockerfile that contains the flag, and a README. The new lab is written
as ``visibility: draft`` so it does not appear for students and does not affect
the prerequisite chain until you publish it.

Examples:
    python3 scripts/new-lab.py --list
    python3 scripts/new-lab.py --track web --level 4 --name "Reflected XSS"
    python3 scripts/new-lab.py --track network --level 3 --name "ARP Spoofing" \
        --difficulty intermediate --category network
    python3 scripts/new-lab.py --track linux --level midterm --name "Blind Pentest"

The script refuses to reuse an existing lab number in the same level, so new
labs always sort after the ones already there instead of tying with them.
"""

import argparse
import ast
import json
import re
import secrets
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LABS_DIR = REPO_ROOT / "platform" / "labs"
SEED_SCRIPT = REPO_ROOT / "platform" / "scripts" / "seed_curriculum.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate-lab.py"

# Track slug -> directory under platform/labs. Mirrors the mapping the
# validator uses in check_track_placement().
TRACK_DIRS = {
    "windows": "Windows",
    "windows-server": "Windows Server",
    "linux": "Linux",
    "web": "Web",
    "network": "Network",
    "malware": "Malware",
    "osint": "OSINT",
    "high-school": "High School",
    "capitalflow": "Capital Flow",
    "forensics": "Forensics",
    "refinery": "Refinery",
}

# Mirrors SLUG_PATTERN in scripts/validate-lab.py.
SLUG_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*-(?:\d+-\d+|midterm-\d+|final-\d+)-[a-z0-9-]+$")


def load_seeded_curriculum(path=SEED_SCRIPT):
    """Return {track_slug: {level_number: level_name}} from the seed script.

    Parsed with ``ast`` instead of imported: the seed script connects to
    PostgreSQL and mutates its own TRACKS list at import time.
    """
    if not path.exists():
        raise SystemExit(f"error: seed script not found: {path}")

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("TRACKS", "EXTRA_LEVELS"):
                    assignments[target.id] = ast.literal_eval(node.value)

    tracks = {}
    for track in assignments.get("TRACKS", []):
        tracks[track["slug"]] = {
            "name": track.get("name", track["slug"]),
            "levels": {
                int(level["level_number"]): level.get("name", "")
                for level in track.get("levels", [])
            },
        }

    for extra in assignments.get("EXTRA_LEVELS", []):
        slug = extra.get("track_slug")
        if slug in tracks:
            tracks[slug]["levels"][int(extra["level_number"])] = extra.get("name", "")

    return tracks


def slugify(text):
    """Lowercase, hyphen-separated slug fragment."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def scan_level(track_dir, track_slug, level_token):
    """Return [(lab_num, dirname)] for labs already in *level_token*."""
    if not track_dir.is_dir():
        return []

    pattern = re.compile(rf"^{re.escape(track_slug)}-{re.escape(level_token)}-(\d+)-")
    found = []
    for entry in sorted(track_dir.iterdir()):
        if not entry.is_dir():
            continue
        match = pattern.match(entry.name)
        if match:
            found.append((int(match.group(1)), entry.name))
    return found


def print_curriculum(tracks, labs_dir):
    """Print seeded levels and how many labs each one already has."""
    print(f"{'track':<10} {'lvl':>4}  {'labs':>4}  level")
    print(f"{'-' * 10} {'-' * 4}  {'-' * 4}  {'-' * 40}")
    for track_slug in sorted(tracks):
        track_dir = labs_dir / TRACK_DIRS.get(track_slug, track_slug.title())
        for level_num in sorted(tracks[track_slug]["levels"]):
            labs = scan_level(track_dir, track_slug, str(level_num))
            marker = "  <- empty" if not labs else ""
            print(
                f"{track_slug:<10} {level_num:>4}  {len(labs):>4}  "
                f"{tracks[track_slug]['levels'][level_num]}{marker}"
            )
    print()
    print("Midterm and final labs are not attached to a level and are always unlocked.")
    print("Use --level midterm or --level final with those.")


def lab_yaml(name, description, difficulty, category, duration, visibility,
             flag, hostname, ip_offset):
    return f"""\
name: {json.dumps(name)}
description: {json.dumps(description)}
difficulty: {difficulty}
category: {category}
duration_minutes: {duration}

# draft keeps the lab out of the student curriculum until you are ready.
# Change to 'public' (or 'course') when the exercise is finished.
visibility: {visibility}

objectives:
  - Replace this objective with what the student actually has to do
  - Capture the flag

scenario: |
  Replace this with the scenario: who the student is, what system they are
  looking at, and why it matters. Keep concrete hostnames and IPs in the
  hostnames and topology sections below rather than hard-coding them here.

hostnames:
  - ip_offset: "{ip_offset}"
    hostname: "{hostname}"
    description: "Scaffold target - rename me"

topology:
  nodes:
    - id: "target"
      label: "Target"
      type: "server"
      ip_offset: "{ip_offset}"
      ports: [80]
      services: ["HTTP"]
      x: 2
      y: 1
  edges:
    - from: "attacker"
      to: "target"
      label: "HTTP:80"
      access: "direct"

# Placeholder flag. It is also written into the target image so the validator
# can confirm the two match. Replace both when you build the real challenge.
flag: "{flag}"

hints:
  - text: |
      Start by identifying the service running on the target and reading the
      page it serves. `curl -v http://{hostname}` shows the headers and body.
    unlock_after_minutes: 0

test:
  steps:
    - name: "Target responds on port 80"
      command: "curl -s -o /dev/null -w '%{{http_code}}' http://{{target.target}}/"
      expect: "200"
    - name: "Retrieve the flag"
      command: "curl -s http://{{target.target}}/flag.txt"
      expect: "{flag}"
"""


def compose_yaml(hostname, ip_offset):
    return f"""\
services:
  target:
    mem_limit: 512m
    cpus: 0.5
    build:
      context: ./containers/target
      dockerfile: Dockerfile
    hostname: {hostname}
    labels:
      ip_offset: "{ip_offset}"
    restart: unless-stopped
"""


def dockerfile(name, flag):
    return f"""\
# Scaffold target for {name}.
# Replace this with the service the exercise actually attacks.
FROM nginx:alpine

# Placeholder flag. Keep this string byte-identical to `flag:` in lab.yaml,
# then move it behind the step the student is meant to perform.
RUN printf '%s\\n' '{flag}' > /usr/share/nginx/html/flag.txt

COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
"""


def index_html(name):
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{name}</title>
</head>
<body>
  <h1>{name}</h1>
  <p>Scaffold target. Replace this page with the service the lab attacks.</p>
</body>
</html>
"""


def readme(slug, track, level_label, labs_dir):
    rel = (labs_dir / TRACK_DIRS.get(track, track.title()) / slug)
    try:
        rel = rel.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = rel.as_posix()
    return f"""\
# {slug}

Scaffold generated by `scripts/new-lab.py`. It is written as `visibility: draft`,
so it is hidden from students and does not gate any other lab.

## What to change

1. `lab.yaml` - scenario, objectives, hints, flag, hostname and topology.
2. `containers/target/` - replace the nginx placeholder with the service the
   exercise attacks, and move the flag behind the intended solve path.
3. Keep `flag:` and the flag written in the Dockerfile byte-identical.

## Validate and publish

```bash
python3 scripts/validate-lab.py {rel}
```

Then load it into the platform by running lab discovery: **Admin -> Scan for
Exercises**, or `python /app/app/scripts/discover_labs.py` in the backend
container. When the exercise is ready, change `visibility` to `public` in
`lab.yaml` and run discovery again.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new OpenCyberRange lab.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1] if "Examples:" in __doc__ else None,
    )
    parser.add_argument("--track", help="Track slug, e.g. web or network")
    parser.add_argument(
        "--level",
        help="Seeded level number, or 'midterm' / 'final'",
    )
    parser.add_argument("--name", help="Human-readable lab name")
    parser.add_argument("--description", default=None, help="One-line lab description")
    parser.add_argument("--lab-num", type=int, default=None, help="Lab number within the level")
    parser.add_argument(
        "--difficulty",
        default="beginner",
        choices=["beginner", "intermediate", "advanced", "expert"],
    )
    parser.add_argument("--category", default="general", help="Lab category (default: general)")
    parser.add_argument("--duration", type=int, default=60, help="Duration in minutes (default: 60)")
    parser.add_argument(
        "--visibility",
        default="draft",
        choices=["draft", "course", "public"],
        help="Initial visibility (default: draft)",
    )
    parser.add_argument(
        "--labs-dir",
        default=str(DEFAULT_LABS_DIR),
        help="Labs root directory (default: platform/labs)",
    )
    parser.add_argument("--no-validate", action="store_true", help="Skip running the validator")
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without writing files")
    parser.add_argument("--list", action="store_true", help="List seeded levels and exit")
    args = parser.parse_args()

    labs_dir = Path(args.labs_dir).resolve()
    tracks = load_seeded_curriculum()

    if args.list:
        print_curriculum(tracks, labs_dir)
        return 0

    missing = [flag for flag in ("track", "level", "name") if not getattr(args, flag)]
    if missing:
        parser.error("required: " + ", ".join("--" + m for m in missing))

    track = args.track.strip().lower()
    if track not in tracks:
        parser.error(
            f"unknown track '{track}'. Seeded tracks: {', '.join(sorted(tracks))}"
        )
    if track not in TRACK_DIRS:
        parser.error(
            f"no directory mapping for track '{track}'. Add it to TRACK_DIRS in this script."
        )

    level_raw = str(args.level).strip().lower()
    if level_raw in ("midterm", "final"):
        level_token = level_raw
        level_label = level_raw
        level_dir = TRACK_DIRS[track]
    else:
        try:
            level_num = int(level_raw)
        except ValueError:
            parser.error("--level must be a number, 'midterm', or 'final'")
        if level_num not in tracks[track]["levels"]:
            seeded = ", ".join(str(n) for n in sorted(tracks[track]["levels"]))
            parser.error(
                f"level {level_num} is not seeded for track '{track}'. "
                f"Seeded levels: {seeded}. Add it to platform/scripts/seed_curriculum.py "
                "first, or use --level midterm / final."
            )
        level_token = str(level_num)
        level_label = f"level {level_num}"
        level_dir = TRACK_DIRS[track]

    name = args.name.strip()
    if not name:
        parser.error("--name must not be empty")

    name_slug = slugify(name)
    if not name_slug:
        parser.error(f"--name '{name}' does not produce a usable slug")

    track_dir = labs_dir / level_dir
    existing = scan_level(track_dir, track, level_token)
    used_nums = {num for num, _ in existing}

    if args.lab_num is not None:
        if args.lab_num < 1:
            parser.error("--lab-num must be positive")
        if args.lab_num in used_nums:
            owners = ", ".join(d for n, d in existing if n == args.lab_num)
            next_free = max(used_nums, default=0) + 1
            parser.error(
                f"lab number {args.lab_num} is already used in {track} {level_label} "
                f"by {owners}; the next free number is {next_free}"
            )
        lab_num = args.lab_num
    else:
        lab_num = max(used_nums, default=0) + 1

    slug = f"{track}-{level_token}-{lab_num}-{name_slug}"
    if not SLUG_RE.match(slug):
        parser.error(f"generated slug '{slug}' does not match the validator pattern")

    lab_dir = track_dir / slug
    if lab_dir.exists():
        parser.error(f"directory already exists: {lab_dir}")

    for existing_dir in labs_dir.rglob(slug):
        if existing_dir.is_dir():
            parser.error(f"a lab with slug '{slug}' already exists: {existing_dir}")

    flag = f"OCR{{scaffold_{secrets.token_hex(4)}}}"
    hostname = f"{name_slug[:32].strip('-') or 'target'}-target"
    ip_offset = "10"
    description = args.description or f"Scaffold exercise: {name}"

    files = {
        lab_dir / "lab.yaml": lab_yaml(
            name=name,
            description=description,
            difficulty=args.difficulty,
            category=args.category,
            duration=args.duration,
            visibility=args.visibility,
            flag=flag,
            hostname=hostname,
            ip_offset=ip_offset,
        ),
        lab_dir / "docker-compose.yml": compose_yaml(hostname, ip_offset),
        lab_dir / "containers" / "target" / "Dockerfile": dockerfile(name, flag),
        lab_dir / "containers" / "target" / "index.html": index_html(name),
        lab_dir / "README.md": readme(slug, track, level_label, labs_dir),
    }

    print(f"Track:    {track} ({tracks[track]['name']})")
    print(f"Level:    {level_label}")
    print(f"Lab:      {name}")
    print(f"Slug:     {slug}")
    print(f"Path:     {lab_dir}")
    print(f"Flag:     {flag}  (placeholder - replace it)")
    print(f"Visible:  {args.visibility}")
    print()

    if args.dry_run:
        print("Dry run - would create:")
        for path in files:
            print(f"  {path.relative_to(labs_dir).as_posix()}")
        return 0

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        print(f"created {path.relative_to(labs_dir).as_posix()}")

    print()
    if args.visibility == "draft":
        print("Draft labs are hidden from students. Set visibility: public in")
        print("lab.yaml when the exercise is ready.")

    if args.no_validate:
        print("Skipped validation (--no-validate).")
        return 0

    print("Running validator...")
    sys.stdout.flush()
    try:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(lab_dir), "--labs-dir", str(labs_dir)],
            cwd=str(REPO_ROOT),
        )
    except OSError as exc:
        print(f"Could not run validator: {exc}", file=sys.stderr)
        return 1

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
