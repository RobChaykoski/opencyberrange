"""Markdown and PDF exports for saved capstone plans.

The export is a document for an instructor or a programme file. It renders the
plan the instructor already reviewed, the validation gate, and the evidence map.
It contains no learner rows, prompts, or model output.
"""

from __future__ import annotations

from fpdf import FPDF

from app.services.pdf_report import _configure_pdf, _sanitize_for_pdf


def _text(value) -> str:
    return "" if value is None else str(value)


def _pct(value) -> str:
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "n/a"


def _hours(value) -> str:
    try:
        return f"{float(value):.1f}h"
    except (TypeError, ValueError):
        return "n/a"


def _file_stem(title: str) -> str:
    cleaned = "".join(
        ch if ch.isalnum() or ch in "-_" else "-" for ch in (title or "").lower()
    )
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return (cleaned or "capstone-plan")[:80]


def export_filename(row: dict, suffix: str) -> str:
    return f"{_file_stem(str(row.get('title') or 'capstone plan'))}.{suffix}"


def _sections(row: dict) -> dict:
    plan = row.get("plan") or {}
    profile = plan.get("profile") or {}
    capstone = profile.get("capstone") or {}
    validation = plan.get("validation") or {}
    return {
        "title": str(row.get("title") or capstone.get("title") or "Capstone plan"),
        "profile": profile,
        "capstone": capstone,
        "request": plan.get("request") or row.get("request") or {},
        "objectives": plan.get("objectives") or [],
        "labs": plan.get("labs") or [],
        "assessments": plan.get("assessments") or [],
        "deliverables": plan.get("deliverables") or [],
        "evidence_map": plan.get("evidence_map") or [],
        "validation": validation,
        "notes": plan.get("notes") or [],
        "status": str(row.get("status") or "draft"),
        "version": row.get("version") or 1,
        "approved_at": row.get("approved_at"),
    }


def _validation_lines(validation: dict) -> list[str]:
    waived = validation.get("waived_competencies") or []
    lines = [
        f"- Coverage: {_pct(validation.get('coverage_percent'))} "
        f"(target {_pct(validation.get('target_coverage_percent'))})",
        f"- Workload: {_hours(validation.get('workload_hours'))} "
        f"(target {_hours(validation.get('target_hours'))})",
        f"- Assessment weights: {_pct(float(validation.get('assessment_weights_total') or 0) * 100)}",
        f"- Prerequisites satisfied: {'yes' if validation.get('prerequisites_satisfied') else 'no'}",
        f"- Publishable: {'yes' if validation.get('publishable') else 'no'}",
    ]
    if waived:
        lines.append(f"- Waived competencies: {', '.join(str(item) for item in waived)}")
        if validation.get("waiver_reason"):
            lines.append(f"- Waiver reason: {_text(validation.get('waiver_reason'))}")
    gaps = validation.get("gaps") or []
    if gaps:
        lines.append("- Uncovered critical competencies:")
        for gap in gaps:
            lines.append(
                f"  - {_text(gap.get('competency_id'))} {_text(gap.get('name'))}"
            )
    return lines


def render_markdown(row: dict) -> str:
    data = _sections(row)
    validation = data["validation"]
    profile = data["profile"]
    capstone = data["capstone"]
    request = data["request"]
    lines: list[str] = []

    lines.append(f"# {data['title']}")
    lines.append("")
    lines.append(
        f"**Profile:** {_text(profile.get('title') or profile.get('id'))}  "
    )
    lines.append(
        f"**Status:** {data['status']}  |  **Version:** {data['version']}  |  "
        f"**Requested:** {_hours(request.get('duration_hours'))}, "
        f"up to {request.get('max_labs', 'n/a')} labs"
    )
    if data["approved_at"]:
        lines.append(f"**Approved:** {data['approved_at']}")
    lines.append("")
    if capstone.get("description"):
        lines.append(_text(capstone.get("description")))
        lines.append("")

    lines.append("## Validation gate")
    lines.extend(_validation_lines(validation))
    lines.append("")

    lines.append("## Objectives")
    for objective in data["objectives"]:
        lines.append(f"{objective.get('number')}. {_text(objective.get('statement'))}")
        competencies = objective.get("competencies") or []
        if competencies:
            labels = ", ".join(
                f"{_text(item.get('id'))} {_text(item.get('name'))}"
                for item in competencies
            )
            lines.append(f"   - Competencies: {labels}")
        evidence = objective.get("evidence_types") or []
        if evidence:
            lines.append(f"   - Evidence: {', '.join(str(item) for item in evidence)}")
    lines.append("")

    lines.append("## Lab sequence")
    lines.append("| # | Lab | Track | Level | Hours | Contract |")
    lines.append("|---:|---|---|---|---:|---|")
    for lab in data["labs"]:
        lines.append(
            f"| {lab.get('order')} | {_text(lab.get('title'))} "
            f"(`{_text(lab.get('slug'))}`) | {_text(lab.get('track'))} | "
            f"{_text(lab.get('difficulty'))} | {_hours(lab.get('hours'))} | "
            f"{'Reviewed' if lab.get('reviewed') else 'Baseline'} |"
        )
    lines.append("")

    lines.append("## Assessments")
    lines.append("| Type | Task | Weight | Rubric | Evidence |")
    lines.append("|---|---|---:|---|---|")
    for item in data["assessments"]:
        weight = float(item.get("weight") or 0) * 100
        lines.append(
            f"| {_text(item.get('type'))} | {_text(item.get('title'))} — "
            f"{_text(item.get('description'))} | {_pct(weight)} | "
            f"{_text(item.get('rubric'))} | {_text(item.get('evidence_type'))} |"
        )
    lines.append("")

    lines.append("## Deliverables")
    lines.append("| # | Deliverable | Evidence | Reviewer |")
    lines.append("|---:|---|---|---|")
    for item in data["deliverables"]:
        lines.append(
            f"| {item.get('number')} | {_text(item.get('title'))} | "
            f"{_text(item.get('evidence_type'))} | {_text(item.get('reviewer'))} |"
        )
    lines.append("")

    lines.append("## Evidence map")
    for item in data["evidence_map"]:
        labs = ", ".join(str(value) for value in (item.get("labs") or []))
        lines.append(
            f"- **{_text(item.get('competency_id'))}** {_text(item.get('name'))} "
            f"via {labs}"
        )
    lines.append("")

    if data["notes"]:
        lines.append("## Notes")
        for note in data["notes"]:
            lines.append(f"- {_text(note)}")
        lines.append("")

    lines.append("---")
    lines.append(
        "Generated by SWOCTS Cyber Range. This plan contains no learner records. "
        "Approval is an instructor decision; publication to a course is a separate step."
    )
    return "\n".join(lines).rstrip() + "\n"


def _pdf_heading(pdf: FPDF, text: str, size: int = 13) -> None:
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", size)
    pdf.multi_cell(0, 7, _sanitize_for_pdf(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)


def _pdf_line(pdf: FPDF, text: str, height: float = 5.5) -> None:
    pdf.multi_cell(0, height, _sanitize_for_pdf(text), new_x="LMARGIN", new_y="NEXT")


def render_pdf(row: dict) -> bytes:
    data = _sections(row)
    validation = data["validation"]
    request = data["request"]
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    _configure_pdf(pdf, data["title"], "Capstone plan")
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 9, _sanitize_for_pdf(data["title"]), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _pdf_line(
        pdf,
        f"Profile: {_text(data['profile'].get('title') or data['profile'].get('id'))}",
    )
    _pdf_line(
        pdf,
        f"Status: {data['status']}  |  Version: {data['version']}  |  "
        f"Requested: {_hours(request.get('duration_hours'))}, "
        f"up to {request.get('max_labs', 'n/a')} labs",
    )
    if data["approved_at"]:
        _pdf_line(pdf, f"Approved: {data['approved_at']}")
    description = _text(data["capstone"].get("description"))
    if description:
        pdf.ln(2)
        _pdf_line(pdf, description)

    _pdf_heading(pdf, "Validation gate")
    for line in _validation_lines(validation):
        _pdf_line(pdf, line)

    _pdf_heading(pdf, "Objectives")
    for objective in data["objectives"]:
        _pdf_line(pdf, f"{objective.get('number')}. {_text(objective.get('statement'))}")
        competencies = objective.get("competencies") or []
        if competencies:
            labels = ", ".join(
                f"{_text(item.get('id'))} {_text(item.get('name'))}"
                for item in competencies
            )
            _pdf_line(pdf, f"   Competencies: {labels}")

    _pdf_heading(pdf, "Lab sequence")
    for lab in data["labs"]:
        _pdf_line(
            pdf,
            f"{lab.get('order')}. {_text(lab.get('title'))} "
            f"({_text(lab.get('slug'))}) - {_text(lab.get('track'))}, "
            f"{_hours(lab.get('hours'))}, "
            f"{'reviewed' if lab.get('reviewed') else 'baseline'}",
        )

    _pdf_heading(pdf, "Assessments")
    for item in data["assessments"]:
        weight = float(item.get("weight") or 0) * 100
        _pdf_line(
            pdf,
            f"{_text(item.get('type'))}: {_text(item.get('title'))} "
            f"({_pct(weight)}, rubric {_text(item.get('rubric'))}, "
            f"evidence {_text(item.get('evidence_type'))})",
        )

    _pdf_heading(pdf, "Deliverables")
    for item in data["deliverables"]:
        _pdf_line(
            pdf,
            f"{item.get('number')}. {_text(item.get('title'))} - "
            f"{_text(item.get('evidence_type'))}, reviewer {_text(item.get('reviewer'))}",
        )

    _pdf_heading(pdf, "Evidence map")
    for item in data["evidence_map"]:
        labs = ", ".join(str(value) for value in (item.get("labs") or []))
        _pdf_line(
            pdf,
            f"{_text(item.get('competency_id'))} {_text(item.get('name'))} via {labs}",
        )

    if data["notes"]:
        _pdf_heading(pdf, "Notes")
        for note in data["notes"]:
            _pdf_line(pdf, f"- {_text(note)}")

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        4.5,
        _sanitize_for_pdf(
            "Generated by SWOCTS Cyber Range. No learner records. "
            "Publication to a course is a separate step."
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    return bytes(pdf.output())
