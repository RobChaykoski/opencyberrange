"""Export the development career profiles as JSON, Markdown, and HTML.

Development/test only:

    python -m app.scripts.export_career_profiles --output-dir data/career_profiles

The export is intentionally a demonstration surface. It reads the learner's
own records and combines Cyber DNA, learning evidence, course participation,
and general external resources. It does not rank learners or predict roles.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from app.database import SessionLocal
from app.models import User
from app.services.career_profile import (
    build_career_dossier,
    render_html,
    render_markdown,
)

DEMO_USERNAMES = (
    "demo_career_ready",
    "demo_career_starting",
    "demo_career_changer",
)


def export_career_profiles(db, output_dir: str) -> list[str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    users = (
        db.query(User)
        .filter(User.username.in_(DEMO_USERNAMES))
        .order_by(User.username.asc())
        .all()
    )
    written = []
    for user in users:
        dossier = build_career_dossier(db, user)
        base = target / user.username
        json_path = base.with_suffix(".json")
        markdown_path = base.with_suffix(".md")
        html_path = base.with_suffix(".html")
        json_path.write_text(
            json.dumps(dossier, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        markdown_path.write_text(render_markdown(dossier), encoding="utf-8")
        html_path.write_text(render_html(dossier), encoding="utf-8")
        written.extend(str(path) for path in (json_path, markdown_path, html_path))
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("CAREER_EXPORT_DIR", "data/career_profiles"),
        help="Directory for JSON, Markdown, and HTML dossiers.",
    )
    args = parser.parse_args()
    db = SessionLocal()
    try:
        written = export_career_profiles(db, args.output_dir)
        if not written:
            print(
                "No career demo profiles found. Run "
                "python -m app.scripts.seed_career_profiles first."
            )
            return
        for path in written:
            print(path)
    finally:
        db.close()


if __name__ == "__main__":
    main()
