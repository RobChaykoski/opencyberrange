import shutil
import subprocess
import sys
from pathlib import Path

import yaml

repo = Path(__file__).resolve().parents[1]
out = repo / "platform" / "frontend" / "wiki.new"
if out.exists():
    shutil.rmtree(out)
(out / "range").mkdir(parents=True)

config = yaml.safe_load((repo / "wikis.yaml").read_text(encoding="utf-8"))
tracks = config.get("tracks", {})
for slug, entry in tracks.items():
    dest = out / "range" / slug
    print(f"building {slug} ({entry['config']})")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "-f",
            entry["config"],
            "--site-dir",
            str(dest),
            "--clean",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
print(f"built {len(tracks)} track wikis into {out}")
