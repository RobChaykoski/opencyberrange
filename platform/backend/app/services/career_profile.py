"""Career-profile dossiers for development and demonstration profiles.

The dossier is an export surface, not a new scoring model. It combines the
learner's Cyber DNA, learning evidence, course participation, and general
external resources into a readable snapshot. It must stay descriptive and
positive: no ranking, no prediction of employability, and no claim that a
learner is ready for a particular job.

This module is used by the development seed/export scripts. It deliberately
reads existing records and does not write learner data.
"""

from __future__ import annotations

import html
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import Achievement, CourseEnrollment, Lab, LabCompletion, Level, User
from app.services.achievements import ACHIEVEMENT_LABELS
from app.services.skill_dna import build_skill_dna


EXTERNAL_RESOURCES = (
    {
        "label": "Security Certification Roadmap (Paul Jerimy)",
        "url": "https://pauljerimy.com/security-certification-roadmap/",
        "use": "Compare certification families and role paths. Verify every requirement with the vendor.",
    },
    {
        "label": "CISO MindMap 2026 (Rafeeq Rehman)",
        "url": "https://rafeeqrehman.com/wp-content/uploads/2026/04/CISO-MindMap-2026.pdf",
        "use": "See how technical work connects to governance, risk, architecture, and leadership.",
    },
    {
        "label": "SWOCTS Resources",
        "url": "https://swocts.com/resources",
        "use": "Find free training, community, and academic entry points that complement the range.",
    },
    {
        "label": "MalOps Peaky Blinders challenge",
        "url": "https://malops.io/challenges/peakyblinders",
        "use": "An external malware-analysis practice reference. It is linked for exploration only; its content is not copied or reproduced here.",
    },
    {
        "label": "Hack The Box Academy",
        "url": "https://academy.hackthebox.com/",
        "use": "External hands-on practice and structured learning paths. Linked as a reference; content is not copied.",
    },
    {
        "label": "PacketLabs",
        "url": "https://www.packetlabs.net/",
        "use": "External penetration-testing and security-research reference. Linked for exploration only.",
    },
    {
        "label": "Cisco Networking Academy",
        "url": "https://www.netacad.com/",
        "use": "External networking and cybersecurity courses. Linked for exploration only.",
    },
)


def _clean_solves(completions: list[LabCompletion]) -> int:
    return sum(
        1 for row in completions
        if (row.hints_used or 0) == 0 and (row.attempts or 1) <= 1
    )


def _rate(part: int, total: int) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _achievement_labels(db: Session, user_id: int) -> list[str]:
    rows = (
        db.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .order_by(Achievement.awarded_at.asc())
        .all()
    )
    labels = []
    for row in rows:
        label = ACHIEVEMENT_LABELS.get(
            row.achievement_type,
            row.achievement_type.replace("_", " ").title(),
        )
        if label not in labels:
            labels.append(label)
    return labels


def _courses(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(CourseEnrollment)
        .options(joinedload(CourseEnrollment.course))
        .filter(CourseEnrollment.user_id == user_id)
        .all()
    )
    return [
        {
            "code": row.course.code,
            "name": row.course.name,
            "semester": row.course.semester,
        }
        for row in rows
        if row.course is not None
    ]


def _completed_labs(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(LabCompletion)
        .options(
            joinedload(LabCompletion.lab)
            .joinedload(Lab.level)
            .joinedload(Level.track)
        )
        .filter(LabCompletion.user_id == user_id)
        .order_by(LabCompletion.completed_at.asc())
        .all()
    )
    result = []
    for row in rows:
        lab = row.lab
        track = lab.level.track if lab and lab.level and lab.level.track else None
        result.append({
            "name": lab.name if lab else "Unknown exercise",
            "category": (lab.category if lab else None) or "general",
            "difficulty": (lab.difficulty if lab else None) or "unknown",
            "track": track.name if track else "Uncategorised",
            "minutes": row.time_spent_minutes or 0,
            "hints": row.hints_used or 0,
            "attempts": row.attempts or 1,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
        })
    return result


def build_career_dossier(db: Session, user: User) -> dict:
    """Build a positive, evidence-based career snapshot for one learner."""
    dna = build_skill_dna(db, user)
    completed = _completed_labs(db, user.id)
    completions = (
        db.query(LabCompletion)
        .filter(LabCompletion.user_id == user.id)
        .all()
    )
    total_minutes = sum(row.time_spent_minutes or 0 for row in completions)
    clean = _clean_solves(completions)
    advanced = sum(
        1 for row in completed
        if str(row["difficulty"]).lower() in {"advanced", "expert"}
    )
    recommended = [row for row in dna["affinities"] if row["recommended"]]
    if not recommended:
        recommended = dna["affinities"][:1]

    next_steps = []
    for affinity in recommended[:2]:
        next_steps.append({
            "title": affinity["label"],
            "action": affinity["next_step"],
            "why": affinity["evidence"],
        })
    if not next_steps:
        next_steps.append({
            "title": "Start with one exercise",
            "action": "Open a beginner exercise and complete it without worrying about the score.",
            "why": "A single completion gives the Cyber DNA model its first evidence.",
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "identity": {
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "organization": user.organization,
            "member_since": user.created_at.isoformat() if user.created_at else None,
        },
        "headline": (
            "A positive, evidence-based snapshot of what this learner has "
            "practised. It is a conversation starter, not a job label."
        ),
        "cyber_dna": {
            "formula_version": dna["formula_version"],
            "overall": dna["overall"],
            "tier": dna["tier"],
            "class": dna["class"],
            "dimensions": dna["dimensions"],
            "affinities": dna["affinities"],
            "equipped_title": dna["titles"]["equipped"]["label"],
        },
        "learning": {
            "completed_exercises": len(completions),
            "started_exercises": dna["signals"]["started_labs"],
            "learning_minutes": total_minutes,
            "learning_hours": round(total_minutes / 60, 1),
            "clean_solves": clean,
            "hint_free_rate": _rate(
                sum(1 for row in completions if (row.hints_used or 0) == 0),
                len(completions),
            ),
            "first_attempt_rate": _rate(
                sum(1 for row in completions if (row.attempts or 1) <= 1),
                len(completions),
            ),
            "advanced_exercises": advanced,
        },
        "courses": _courses(db, user.id),
        "achievements": _achievement_labels(db, user.id),
        "recommended_next_steps": next_steps,
        "external_resources": list(EXTERNAL_RESOURCES),
        "reflection_questions": [
            "Which activity felt most energising: finding a way in, defending a system, investigating evidence, or leading a group?",
            "Which recommended next step can you try in the next two weeks?",
            "What evidence would you want to show an instructor, mentor, or employer after that step?",
        ],
        "privacy_note": (
            "This dossier contains the learner's own activity. Do not use it for "
            "admissions, hiring, ranking, or high-stakes decisions. Career "
            "affinities are practice signals, not predictions."
        ),
    }


def render_markdown(dossier: dict) -> str:
    dna = dossier["cyber_dna"]
    learning = dossier["learning"]
    lines = [
        f"# Career profile: {dossier['identity']['display_name']}",
        "",
        dossier["headline"],
        "",
        "## At a glance",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Username | {dossier['identity']['username']} |",
        f"| Organisation | {dossier['identity']['organization'] or 'Not set'} |",
        f"| Cyber DNA class | {dna['class']['class_name']} ({dna['class']['label']}) |",
        f"| Overall tier | {dna['tier']} |",
        f"| Completed exercises | {learning['completed_exercises']} |",
        f"| Learning time | {learning['learning_hours']} hours |",
        f"| Clean solves | {learning['clean_solves']} |",
        "",
        "## Cyber DNA traits",
        "",
        "| Trait | Class | Tier | Score | Evidence |",
        "|---|---|---|---:|---|",
    ]
    for row in dna["dimensions"]:
        lines.append(
            f"| {row['label']} | {row['class_name']} | {row['tier']} | "
            f"{row['score']} | {row['evidence']} |"
        )
    lines.extend([
        "",
        "## Practice affinities",
        "",
        "| Affinity | Evidence | Recommended |",
        "|---|---|---|",
    ])
    for row in dna["affinities"]:
        lines.append(
            f"| {row['label']} | {row['evidence']} ({row['evidence_level'].replace('_', ' ')}) | "
            f"{'Yes' if row['recommended'] else 'No'} |"
        )
    lines.extend([
        "",
        "## Recommended next steps",
        "",
    ])
    for step in dossier["recommended_next_steps"]:
        lines.append(f"- **{step['title']}:** {step['action']}  ")
        lines.append(f"  Why: {step['why']}")
    lines.extend([
        "",
        "## Courses",
        "",
    ])
    if dossier["courses"]:
        for course in dossier["courses"]:
            lines.append(f"- {course['code']} · {course['name']} ({course['semester']})")
    else:
        lines.append("- No course enrolment yet.")
    lines.extend([
        "",
        "## Achievements",
        "",
    ])
    if dossier["achievements"]:
        for label in dossier["achievements"]:
            lines.append(f"- {label}")
    else:
        lines.append("- No achievements yet.")
    lines.extend([
        "",
        "## Reflection questions",
        "",
    ])
    for question in dossier["reflection_questions"]:
        lines.append(f"- {question}")
    lines.extend([
        "",
        "## External resources",
        "",
        "These links are references, not copies of their content.",
        "",
    ])
    for resource in dossier["external_resources"]:
        lines.append(f"- [{resource['label']}]({resource['url']}) — {resource['use']}")
    lines.extend([
        "",
        "## Privacy",
        "",
        dossier["privacy_note"],
        "",
    ])
    return "\n".join(lines)


def render_html(dossier: dict) -> str:
    def esc(value) -> str:
        return html.escape(str(value or ""))

    dna = dossier["cyber_dna"]
    learning = dossier["learning"]
    trait_rows = "".join(
        f"<tr><th scope=\"row\">{esc(row['label'])}</th>"
        f"<td>{esc(row['class_name'])}</td><td>{esc(row['tier'])}</td>"
        f"<td class=\"num\">{row['score']}</td><td>{esc(row['evidence'])}</td></tr>"
        for row in dna["dimensions"]
    )
    affinity_rows = "".join(
        f"<article class=\"affinity{' recommended' if row['recommended'] else ''}\">"
        f"<div class=\"affinity-head\"><strong>{esc(row['label'])}</strong>"
        f"<span>{esc(row['evidence_level'].replace('_', ' '))}</span></div>"
        f"<p>{esc(row['summary'])}</p><p class=\"evidence\">{esc(row['evidence'])}</p>"
        f"<p><strong>Next:</strong> {esc(row['next_step'])}</p>"
        f"<p class=\"roles\"><strong>Roles:</strong> {esc(', '.join(row['roles']))}</p>"
        f"</article>"
        for row in dna["affinities"]
    )
    next_steps = "".join(
        f"<li><strong>{esc(step['title'])}:</strong> {esc(step['action'])}"
        f"<br><span class=\"muted\">Why: {esc(step['why'])}</span></li>"
        for step in dossier["recommended_next_steps"]
    )
    courses = "".join(
        f"<li>{esc(course['code'])} · {esc(course['name'])} ({esc(course['semester'])})</li>"
        for course in dossier["courses"]
    ) or "<li>No course enrolment yet.</li>"
    achievements = "".join(
        f"<li>{esc(label)}</li>" for label in dossier["achievements"]
    ) or "<li>No achievements yet.</li>"
    questions = "".join(
        f"<li>{esc(question)}</li>" for question in dossier["reflection_questions"]
    )
    resources = "".join(
        f"<li><a href=\"{esc(resource['url'])}\" rel=\"noopener noreferrer\">"
        f"{esc(resource['label'])}</a><br><span class=\"muted\">{esc(resource['use'])}</span></li>"
        for resource in dossier["external_resources"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Career profile: {esc(dossier['identity']['display_name'])}</title>
<style>
  :root {{ color-scheme: dark; --bg:#0f172a; --panel:#1e293b; --line:#334155;
    --text:#f8fafc; --muted:#94a3b8; --accent:#3b82f6; --success:#22c55e; --warning:#f59e0b; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:2rem; background:var(--bg); color:var(--text);
    font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ max-width: 1080px; margin: 0 auto; }}
  h1,h2 {{ line-height:1.2; }}
  h1 {{ margin:0 0 .35rem; font-size:2rem; }}
  h2 {{ margin:1.8rem 0 .65rem; font-size:1.1rem; }}
  .eyebrow {{ margin:0 0 .35rem; color:var(--accent); font-size:.7rem; font-weight:700;
    letter-spacing:.12em; text-transform:uppercase; }}
  .muted {{ color:var(--muted); }}
  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    gap:.65rem; margin:1.25rem 0; }}
  .stat, .panel, .affinity {{ border:1px solid var(--line); background:var(--panel); border-radius:10px; }}
  .stat {{ padding:.8rem; }}
  .stat strong {{ display:block; font-size:1.35rem; }}
  .stat span {{ color:var(--muted); font-size:.75rem; }}
  .panel {{ padding:1rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  th,td {{ padding:.45rem .5rem; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
  thead th {{ color:var(--muted); font-size:.7rem; text-transform:uppercase; letter-spacing:.05em; }}
  .num {{ font-variant-numeric:tabular-nums; text-align:right; }}
  .affinities {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:.65rem; }}
  .affinity {{ padding:.85rem; }}
  .affinity.recommended {{ border-color:var(--accent); box-shadow:inset 0 0 0 1px var(--accent); }}
  .affinity-head {{ display:flex; justify-content:space-between; gap:.5rem; align-items:flex-start; }}
  .affinity-head span {{ flex:0 0 auto; padding:.15rem .4rem; border-radius:999px;
    background:rgba(59,130,246,.15); color:var(--accent); font-size:.62rem;
    font-weight:700; text-transform:uppercase; letter-spacing:.04em; }}
  .affinity p {{ margin:.35rem 0; font-size:.8rem; color:var(--muted); }}
  .affinity .evidence {{ color:var(--text); }}
  ul {{ margin:.4rem 0; padding-left:1.25rem; }}
  li {{ margin:.35rem 0; }}
  a {{ color:var(--accent); }}
  footer {{ margin-top:2rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font-size:.75rem; }}
  @media print {{ :root {{ color-scheme: light; --bg:#fff; --panel:#fff; --line:#d8dee9;
    --text:#111827; --muted:#4b5563; --accent:#1d4ed8; }}
    body {{ padding:0; }} .affinity, .stat, .panel {{ break-inside:avoid; }} }}
</style>
</head>
<body>
<main>
  <p class="eyebrow">SWOCTS Cyber Range · Career profile</p>
  <h1>{esc(dossier['identity']['display_name'])}</h1>
  <p class="muted">@{esc(dossier['identity']['username'])} · {esc(dossier['identity']['organization'] or 'Organisation not set')} · generated {esc(dossier['generated_at'][:10])}</p>
  <p>{esc(dossier['headline'])}</p>

  <div class="stats">
    <div class="stat"><strong>{esc(dna['class']['class_name'])}</strong><span>Cyber DNA class</span></div>
    <div class="stat"><strong>{dna['overall']}</strong><span>Overall score · {esc(dna['tier'])}</span></div>
    <div class="stat"><strong>{learning['completed_exercises']}</strong><span>Completed exercises</span></div>
    <div class="stat"><strong>{learning['learning_hours']} h</strong><span>Learning time</span></div>
    <div class="stat"><strong>{learning['clean_solves']}</strong><span>Clean solves</span></div>
  </div>

  <h2>Cyber DNA traits</h2>
  <div class="panel"><table>
    <thead><tr><th scope="col">Trait</th><th scope="col">Class</th><th scope="col">Tier</th><th scope="col">Score</th><th scope="col">Evidence</th></tr></thead>
    <tbody>{trait_rows}</tbody>
  </table></div>

  <h2>Practice affinities</h2>
  <div class="affinities">{affinity_rows}</div>

  <h2>Recommended next steps</h2>
  <ul>{next_steps}</ul>

  <h2>Courses</h2>
  <ul>{courses}</ul>

  <h2>Achievements</h2>
  <ul>{achievements}</ul>

  <h2>Reflection questions</h2>
  <ul>{questions}</ul>

  <h2>External resources</h2>
  <p class="muted">These links are references, not copies of their content. Verify requirements and availability with the source.</p>
  <ul>{resources}</ul>

  <footer>{esc(dossier['privacy_note'])}</footer>
</main>
</body>
</html>
"""
