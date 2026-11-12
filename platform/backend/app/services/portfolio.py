"""Professional portfolio and employer-ready skills transcript.

The portfolio is an evidence surface, not a new score. It combines the learner's
Cyber DNA, competency axes, work samples, capstones, certificates, and career
direction into a readable, printable record.

It must stay descriptive and positive: no ranking, no prediction of
employability, and no claim that the learner is ready for a particular job.
"""

from __future__ import annotations

import hashlib
import html
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User
from app.services.competency_model import AXES
from app.services.competency_radar import build_individual_radar

AXIS_CAREER_FAMILIES = {
    "network_systems": ["defensive", "cloud", "ot"],
    "web_api": ["appsec", "offensive"],
    "identity_access": ["identity", "defensive"],
    "incident_forensics": ["investigative", "defensive"],
    "osint": ["intel", "investigative"],
    "malware": ["investigative"],
    "ot_ics": ["ot"],
    "ai_security": ["ai"],
}

EVIDENCE_LABELS = {
    "insufficient": "No evidence yet",
    "early": "Early evidence",
    "growing": "Growing evidence",
    "strong": "Strong evidence",
}

DIFFICULTY_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}


def _iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return value.isoformat()


def _rate(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _clean(item: dict) -> bool:
    return (item.get("hints_used") or 0) == 0 and (item.get("attempts") or 1) <= 1


def _difficulty_rank(value) -> int:
    return DIFFICULTY_RANK.get(str(value or "").lower(), 0)


def _is_capstone(item: dict) -> bool:
    text = " ".join(
        str(item.get(field) or "")
        for field in ("lab_name", "lab_slug", "workbook", "category")
    ).lower()
    return "capstone" in text or "assessment" in text or "final exam" in text


def _skills(radar: dict) -> list[dict]:
    axes = {axis["key"]: axis for axis in radar.get("axes", [])}
    rows = []
    for spec in AXES:
        axis = axes.get(spec["key"], {})
        evidence_level = axis.get("evidence_quality") or "insufficient"
        rows.append(
            {
                "key": spec["key"],
                "label": spec["label"],
                "description": spec["description"],
                "score": axis.get("score"),
                "current": axis.get("current"),
                "target": axis.get("target"),
                "evidence_level": evidence_level,
                "evidence_label": EVIDENCE_LABELS.get(evidence_level, "Evidence"),
                "evidence_count": axis.get("evidence_count", 0),
                "career_families": AXIS_CAREER_FAMILIES.get(spec["key"], []),
            }
        )
    return rows


def _capstones(completions: list[dict]) -> list[dict]:
    rows = []
    for item in completions:
        if not _is_capstone(item):
            continue
        rows.append(
            {
                "name": item.get("lab_name"),
                "track": item.get("track_name"),
                "difficulty": item.get("difficulty"),
                "completed_at": item.get("completed_at"),
                "clean_solve": _clean(item),
                "minutes": item.get("time_spent_minutes") or 0,
                "workbook": item.get("workbook"),
            }
        )
    rows.sort(key=lambda row: row.get("completed_at") or "", reverse=True)
    return rows[:6]


def _work_samples(completions: list[dict]) -> list[dict]:
    ranked = sorted(
        completions,
        key=lambda item: (
            0 if _clean(item) else 1,
            -_difficulty_rank(item.get("difficulty")),
            str(item.get("completed_at") or ""),
        ),
        reverse=False,
    )
    rows = []
    for item in ranked[:6]:
        rows.append(
            {
                "name": item.get("lab_name"),
                "track": item.get("track_name"),
                "difficulty": item.get("difficulty"),
                "completed_at": item.get("completed_at"),
                "clean_solve": _clean(item),
                "minutes": item.get("time_spent_minutes") or 0,
                "workbook": item.get("workbook"),
                "primary_competency": item.get("primary_competency"),
            }
        )
    return rows


def _workbooks(completions: list[dict]) -> list[dict]:
    seen = {}
    for item in completions:
        workbook = item.get("workbook")
        if not workbook:
            continue
        seen[workbook] = {
            "workbook": workbook,
            "lab": item.get("lab_name"),
            "track": item.get("track_name"),
            "chapter": item.get("chapter_label"),
            "completed_at": item.get("completed_at"),
        }
    rows = list(seen.values())
    rows.sort(key=lambda row: row.get("completed_at") or "", reverse=True)
    return rows[:12]


def _learning(completions: list[dict], summary: dict, capstones: list[dict], workbooks: list[dict]) -> dict:
    total_minutes = sum(item.get("time_spent_minutes") or 0 for item in completions)
    clean = sum(1 for item in completions if _clean(item))
    advanced = sum(
        1
        for item in completions
        if str(item.get("difficulty") or "").lower() in {"advanced", "expert"}
    )
    started = (summary.get("skill_dna") or {}).get("signals", {}).get("started_labs")
    return {
        "completed_exercises": len(completions),
        "started_exercises": started if started is not None else len(completions),
        "learning_minutes": total_minutes,
        "learning_hours": round(total_minutes / 60, 1),
        "clean_solves": clean,
        "hint_free_rate": _rate(
            sum(1 for item in completions if (item.get("hints_used") or 0) == 0),
            len(completions),
        ),
        "first_attempt_rate": _rate(
            sum(1 for item in completions if (item.get("attempts") or 1) <= 1),
            len(completions),
        ),
        "advanced_exercises": advanced,
        "workbooks_completed": len(workbooks),
        "capstones_completed": len(capstones),
        "certificates": len(summary.get("certificates") or []),
        "achievements": len(summary.get("achievements") or []),
        "tracks_practised": len({item.get("track_slug") for item in completions if item.get("track_slug")}),
    }


def _career_pathway(dna: dict) -> dict | None:
    atlas = dna.get("career_atlas")
    if not atlas:
        return None
    families = {family["key"]: family for family in atlas.get("families", [])}
    recommended = families.get(atlas.get("recommended_family_key") or "")
    if recommended is None:
        recommended = next(
            (family for family in atlas.get("families", []) if family.get("recommended")),
            None,
        )
    if recommended is None:
        return None
    roles = [
        {
            "title": role.get("title"),
            "level": role.get("level"),
            "summary": role.get("summary"),
        }
        for role in recommended.get("roles", [])
    ]
    return {
        "recommended_family": {
            "key": recommended.get("key"),
            "label": recommended.get("label"),
            "summary": recommended.get("summary"),
            "branch_label": recommended.get("branch_label"),
            "unlock_state": recommended.get("unlock_state"),
            "match_score": recommended.get("match_score"),
            "next_step": recommended.get("next_step"),
            "roles": roles,
        },
        "salary_note": (
            "Salary bands are intentionally omitted from the employer transcript. "
            "They are national planning ranges, not an offer or a prediction."
        ),
    }


def _content_hash(payload: dict) -> str:
    material = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def build_portfolio(db: Session, user: User, summary: dict) -> dict:
    """Build the learner's professional portfolio payload."""
    dna = summary.get("skill_dna") or {}
    radar = build_individual_radar(db, user.id)
    completions = summary.get("completions") or []
    capstones = _capstones(completions)
    workbooks = _workbooks(completions)
    portfolio_id = str(uuid.uuid4())
    generated_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "generated_at": generated_at,
        "portfolio_id": portfolio_id,
        "headline": (
            "A professional, evidence-based portfolio of practice. It is a "
            "conversation aid, not a grade, a ranking, or a hiring prediction."
        ),
        "identity": {
            "display_name": user.display_name,
            "username": user.username,
            "organization": user.organization,
            "member_since": _iso(user.created_at),
        },
        "cyber_dna": {
            "formula_version": dna.get("formula_version"),
            "overall": dna.get("overall"),
            "tier": dna.get("tier"),
            "class": dna.get("class"),
            "dimensions": dna.get("dimensions", []),
            "affinities": dna.get("affinities", []),
            "equipped_title": (dna.get("titles") or {}).get("equipped", {}).get("label"),
        },
        "momentum": dna.get("momentum"),
        "career_pathway": _career_pathway(dna),
        "skills": _skills(radar),
        "learning": _learning(completions, summary, capstones, workbooks),
        "capstones": capstones,
        "workbooks": workbooks,
        "work_samples": _work_samples(completions),
        "certificates": summary.get("certificates") or [],
        "achievements": summary.get("achievements") or [],
        "privacy_note": (
            "This portfolio contains the learner's own activity. Do not use it for "
            "admissions, hiring, ranking, or high-stakes decisions without the "
            "learner's consent and a human review of the evidence."
        ),
        "verification": {
            "portfolio_id": portfolio_id,
            "sha256": None,
            "note": (
                "Re-download the portfolio from the learner's account to compare "
                "the SHA-256. External verification is a planned follow-up."
            ),
        },
    }
    payload["verification"]["sha256"] = _content_hash(payload)
    return payload


def _money_none(value) -> str:
    return "—" if value is None else str(value)


def render_markdown(portfolio: dict) -> str:
    dna = portfolio["cyber_dna"]
    learning = portfolio["learning"]
    skills = portfolio["skills"]
    lines = [
        f"# Professional portfolio: {portfolio['identity']['display_name']}",
        "",
        portfolio["headline"],
        "",
        "## At a glance",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Portfolio ID | `{portfolio['portfolio_id']}` |",
        f"| Generated | {portfolio['generated_at'][:10]} |",
        f"| Cyber DNA class | {dna['class']['class_name']} ({dna['class']['label']}) |",
        f"| Overall tier | {dna['tier']} |",
        f"| Completed exercises | {learning['completed_exercises']} |",
        f"| Learning time | {learning['learning_hours']} hours |",
        f"| Workbooks completed | {learning['workbooks_completed']} |",
        f"| Capstones completed | {learning['capstones_completed']} |",
        f"| Certificates | {learning['certificates']} |",
        "",
        "## Cyber DNA",
        "",
        "| Trait | Class | Tier | Score | Evidence |",
        "|---|---|---|---:|---|",
    ]
    for row in dna["dimensions"]:
        lines.append(
            f"| {row['label']} | {row['class_name']} | {row['tier']} | "
            f"{row['score']} | {row['evidence']} |"
        )
    lines.extend(["", "## Skills catalogue", "", "| Skill | Score | Evidence | Career families |", "|---|---:|---|---|"])
    for skill in skills:
        lines.append(
            f"| {skill['label']} | {_money_none(skill['score'])} | "
            f"{skill['evidence_label']} ({skill['evidence_count']}) | "
            f"{', '.join(skill['career_families']) or '—'} |"
        )
    if portfolio.get("career_pathway"):
        family = portfolio["career_pathway"]["recommended_family"]
        lines.extend([
            "",
            "## Career direction",
            "",
            f"**{family['label']}** · {family['branch_label']} branch · "
            f"{family['unlock_state'].replace('_', ' ')} · match {family['match_score']}/100",
            "",
            family["summary"],
            "",
            f"**Next practice step:** {family['next_step']}",
            "",
            "| Role | Level |",
            "|---|---|",
        ])
        for role in family["roles"]:
            lines.append(f"| {role['title']} | {role['level']} |")
    lines.extend(["", "## Capstones", ""])
    if portfolio["capstones"]:
        lines.append("| Capstone | Track | Difficulty | Completed | Clean |")
        lines.append("|---|---|---|---|---|")
        for row in portfolio["capstones"]:
            lines.append(
                f"| {row['name']} | {row['track']} | {row['difficulty']} | "
                f"{(row['completed_at'] or '')[:10]} | {'Yes' if row['clean_solve'] else 'No'} |"
            )
    else:
        lines.append("No capstone evidence yet.")
    lines.extend(["", "## Work samples", ""])
    for row in portfolio["work_samples"]:
        lines.append(
            f"- **{row['name']}** ({row['track']}, {row['difficulty']}) · "
            f"{(row['completed_at'] or '')[:10]} · "
            f"{'clean solve' if row['clean_solve'] else 'completed'}"
        )
    lines.extend(["", "## Certificates", ""])
    if portfolio["certificates"]:
        for cert in portfolio["certificates"]:
            lines.append(
                f"- {cert.get('track_name')} · Level {cert.get('level_number')}: "
                f"{cert.get('level_name')} · {cert.get('certificate_id')}"
            )
    else:
        lines.append("No certificates yet.")
    lines.extend([
        "",
        "## Verification",
        "",
        f"Portfolio ID: `{portfolio['portfolio_id']}`",
        "",
        f"SHA-256: `{portfolio['verification']['sha256']}`",
        "",
        portfolio["verification"]["note"],
        "",
        "## Privacy",
        "",
        portfolio["privacy_note"],
        "",
    ])
    return "\n".join(lines)


def render_html(portfolio: dict) -> str:
    def esc(value) -> str:
        return html.escape(str(value or ""))

    dna = portfolio["cyber_dna"]
    learning = portfolio["learning"]
    skills = portfolio["skills"]
    trait_rows = "".join(
        f"<tr><th scope=\"row\">{esc(row['label'])}</th>"
        f"<td>{esc(row['class_name'])}</td><td>{esc(row['tier'])}</td>"
        f"<td class=\"num\">{row['score']}</td><td>{esc(row['evidence'])}</td></tr>"
        for row in dna["dimensions"]
    )
    skill_cards = "".join(
        f"<article class=\"skill\">"
        f"<div class=\"skill-head\"><strong>{esc(skill['label'])}</strong>"
        f"<span>{esc(skill['evidence_label'])}</span></div>"
        f"<p>{esc(skill['description'])}</p>"
        f"<div class=\"bar\"><span style=\"width:{max(0, min(100, skill['score'] or 0))}%\"></span></div>"
        f"<p class=\"muted\">Score: {esc(_money_none(skill['score']))} · "
        f"Evidence: {skill['evidence_count']} · "
        f"Career families: {esc(', '.join(skill['career_families']) or '—')}</p>"
        f"</article>"
        for skill in skills
    )
    capstone_rows = "".join(
        f"<tr><th scope=\"row\">{esc(row['name'])}</th><td>{esc(row['track'])}</td>"
        f"<td>{esc(row['difficulty'])}</td><td>{(row['completed_at'] or '')[:10]}</td>"
        f"<td>{'Yes' if row['clean_solve'] else 'No'}</td></tr>"
        for row in portfolio["capstones"]
    ) or "<tr><td colspan=\"5\">No capstone evidence yet.</td></tr>"
    work_samples = "".join(
        f"<li><strong>{esc(row['name'])}</strong> ({esc(row['track'])}, "
        f"{esc(row['difficulty'])}) · {(row['completed_at'] or '')[:10]} · "
        f"{'clean solve' if row['clean_solve'] else 'completed'}</li>"
        for row in portfolio["work_samples"]
    ) or "<li>No work samples yet.</li>"
    certificates = "".join(
        f"<li>{esc(cert.get('track_name'))} · Level {esc(cert.get('level_number'))}: "
        f"{esc(cert.get('level_name'))} · <code>{esc(cert.get('certificate_id'))}</code></li>"
        for cert in portfolio["certificates"]
    ) or "<li>No certificates yet.</li>"
    career = portfolio.get("career_pathway")
    career_html = ""
    if career:
        family = career["recommended_family"]
        roles = "".join(
            f"<li><strong>{esc(role['title'])}</strong> · {esc(role['level'])}</li>"
            for role in family["roles"]
        )
        career_html = f"""
        <h2>Career direction</h2>
        <div class="panel">
          <p class="eyebrow">{esc(family['branch_label'])} branch · {esc(family['unlock_state'].replace('_', ' '))} · match {family['match_score']}/100</p>
          <h3>{esc(family['label'])}</h3>
          <p>{esc(family['summary'])}</p>
          <p><strong>Next practice step:</strong> {esc(family['next_step'])}</p>
          <ul>{roles}</ul>
          <p class="muted">{esc(career['salary_note'])}</p>
        </div>
        """
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Professional portfolio: {esc(portfolio['identity']['display_name'])}</title>
<style>
  :root {{ color-scheme: dark; --bg:#0f172a; --panel:#1e293b; --line:#334155;
    --text:#f8fafc; --muted:#94a3b8; --accent:#3b82f6; --success:#22c55e; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:2rem; background:var(--bg); color:var(--text);
    font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ max-width: 1080px; margin: 0 auto; }}
  h1,h2,h3 {{ line-height:1.2; }}
  h1 {{ margin:0 0 .35rem; font-size:2rem; }}
  h2 {{ margin:1.8rem 0 .65rem; font-size:1.1rem; }}
  .eyebrow {{ margin:0 0 .35rem; color:var(--accent); font-size:.7rem; font-weight:700;
    letter-spacing:.12em; text-transform:uppercase; }}
  .muted {{ color:var(--muted); }}
  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    gap:.65rem; margin:1.25rem 0; }}
  .stat, .panel, .skill {{ border:1px solid var(--line); background:var(--panel); border-radius:10px; }}
  .stat {{ padding:.8rem; }}
  .stat strong {{ display:block; font-size:1.35rem; }}
  .stat span {{ color:var(--muted); font-size:.75rem; }}
  .panel {{ padding:1rem; }}
  .skills {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:.65rem; }}
  .skill {{ padding:.85rem; }}
  .skill-head {{ display:flex; justify-content:space-between; gap:.5rem; align-items:flex-start; }}
  .skill-head span {{ flex:0 0 auto; color:var(--accent); font-size:.62rem; font-weight:700; text-transform:uppercase; }}
  .skill p {{ margin:.35rem 0; font-size:.78rem; color:var(--muted); }}
  .bar {{ height:6px; margin:.4rem 0; border-radius:999px; background:#0b1220; overflow:hidden; }}
  .bar span {{ display:block; height:100%; border-radius:inherit; background:var(--accent); }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  th,td {{ padding:.45rem .5rem; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
  thead th {{ color:var(--muted); font-size:.7rem; text-transform:uppercase; letter-spacing:.05em; }}
  .num {{ font-variant-numeric:tabular-nums; text-align:right; }}
  ul {{ margin:.4rem 0; padding-left:1.25rem; }}
  li {{ margin:.35rem 0; }}
  a {{ color:var(--accent); }}
  code {{ font-family:"JetBrains Mono",ui-monospace,monospace; font-size:.8em; }}
  footer {{ margin-top:2rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font-size:.75rem; }}
  @media print {{ :root {{ color-scheme: light; --bg:#fff; --panel:#fff; --line:#d8dee9;
    --text:#111827; --muted:#4b5563; --accent:#1d4ed8; }}
    body {{ padding:0; }} .skill, .stat, .panel {{ break-inside:avoid; }} }}
</style>
</head>
<body>
<main>
  <p class="eyebrow">SWOCTS Cyber Range · Professional portfolio</p>
  <h1>{esc(portfolio['identity']['display_name'])}</h1>
  <p class="muted">@{esc(portfolio['identity']['username'])} · {esc(portfolio['identity']['organization'] or 'Organisation not set')} · generated {esc(portfolio['generated_at'][:10])}</p>
  <p>{esc(portfolio['headline'])}</p>

  <div class="stats">
    <div class="stat"><strong>{esc(dna['class']['class_name'])}</strong><span>Cyber DNA class</span></div>
    <div class="stat"><strong>{dna['overall']}</strong><span>Overall · {esc(dna['tier'])}</span></div>
    <div class="stat"><strong>{learning['completed_exercises']}</strong><span>Completed exercises</span></div>
    <div class="stat"><strong>{learning['learning_hours']} h</strong><span>Learning time</span></div>
    <div class="stat"><strong>{learning['capstones_completed']}</strong><span>Capstones</span></div>
    <div class="stat"><strong>{learning['certificates']}</strong><span>Certificates</span></div>
  </div>

  <h2>Cyber DNA</h2>
  <div class="panel"><table>
    <thead><tr><th scope="col">Trait</th><th scope="col">Class</th><th scope="col">Tier</th><th scope="col">Score</th><th scope="col">Evidence</th></tr></thead>
    <tbody>{trait_rows}</tbody>
  </table></div>

  <h2>Skills catalogue</h2>
  <div class="skills">{skill_cards}</div>

  {career_html}

  <h2>Capstones</h2>
  <div class="panel"><table>
    <thead><tr><th scope="col">Capstone</th><th scope="col">Track</th><th scope="col">Difficulty</th><th scope="col">Completed</th><th scope="col">Clean</th></tr></thead>
    <tbody>{capstone_rows}</tbody>
  </table></div>

  <h2>Work samples</h2>
  <ul>{work_samples}</ul>

  <h2>Certificates</h2>
  <ul>{certificates}</ul>

  <h2>Verification</h2>
  <div class="panel">
    <p>Portfolio ID: <code>{esc(portfolio['portfolio_id'])}</code></p>
    <p>SHA-256: <code>{esc(portfolio['verification']['sha256'])}</code></p>
    <p class="muted">{esc(portfolio['verification']['note'])}</p>
  </div>

  <footer>{esc(portfolio['privacy_note'])}</footer>
</main>
</body>
</html>
"""
