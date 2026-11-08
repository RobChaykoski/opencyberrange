"""Cross-course learning report PDF for instructors and administrators."""
from __future__ import annotations

from datetime import datetime
from fpdf import FPDF

from app.services.pdf_report import _sanitize_for_pdf


class LearningReportPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=14)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, "SWOCTS Cyber Range - Learning reports", ln=True, align="R")
        self.set_text_color(30, 41, 59)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")


def _cell(pdf: FPDF, width: float, text: str, *, bold: bool = False, align: str = "L", fill: bool = False):
    pdf.set_font("Helvetica", "B" if bold else "", 8)
    pdf.cell(width, 7, _sanitize_for_pdf(str(text)), border=1, align=align, fill=fill)


def generate_reports_pdf(payload: dict) -> bytes:
    """Render the cross-course report used by the Reports page.

    The PDF follows the same aggregate-only rule as the web page: it contains
    course totals and teaching signals, never individual learner names.
    """
    rows = payload.get("courses", [])
    totals = payload.get("totals", {})
    generated_at = payload.get("generated_at")
    try:
        generated_label = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError):
        generated_label = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    pdf = LearningReportPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "Learning reports", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, f"Generated {generated_label}", ln=True)
    pdf.ln(3)

    summary = [
        ("Courses", totals.get("courses", 0)),
        ("Learners", totals.get("enrolled_learners", 0)),
        ("Learning hours", totals.get("total_learning_hours", 0)),
        ("Pulse responses", totals.get("pulse_responses", 0)),
        ("Exercise feedback", f"{totals.get('positive_rate', 0)}% positive"),
    ]
    box_width = 48
    for label, value in summary:
        pdf.set_fill_color(241, 245, 249)
        pdf.set_draw_color(203, 213, 225)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(box_width, 6, _sanitize_for_pdf(label.upper()), border=1, fill=True)
    pdf.ln(6)
    for _label, value in summary:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(box_width, 9, _sanitize_for_pdf(str(value)), border=1, align="C")
    pdf.ln(9)

    suppressed_courses = totals.get("suppressed_courses", 0)
    no_evidence_courses = totals.get("no_evidence_courses", 0)
    minimum_cohort = totals.get("minimum_cohort_size", 0)
    if suppressed_courses or no_evidence_courses:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.multi_cell(
            0,
            5,
            _sanitize_for_pdf(
                f"{suppressed_courses} course(s) suppressed; "
                f"{no_evidence_courses} course(s) with no evidence. "
                f"Minimum reporting cohort is {minimum_cohort} learners."
            ),
        )
    pdf.ln(4)

    skill_tree = totals.get("skill_tree") or {}
    if skill_tree.get("dimensions"):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 7, "Skill tree coverage", ln=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(
            0,
            5,
            _sanitize_for_pdf(
                "Assigned and completed exercises by Skill DNA branch. "
                "Shares are the mix of exercises, not learner scores."
            ),
            ln=True,
        )
        pdf.ln(1)
        skill_headers = [
            ("Branch", 52), ("Assigned", 24), ("Share", 22),
            ("Completed", 28), ("Share", 22),
        ]
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        for title, width in skill_headers:
            _cell(pdf, width, title, bold=True, align="C", fill=True)
        pdf.ln(7)
        for index, dimension in enumerate(skill_tree["dimensions"]):
            values = [
                dimension.get("label") or dimension.get("key") or "",
                dimension.get("assigned", 0),
                f"{dimension.get('assigned_pct', 0)}%",
                dimension.get("completed", 0),
                f"{dimension.get('completed_pct', 0)}%",
            ]
            fill = index % 2 == 0
            if fill:
                pdf.set_fill_color(248, 250, 252)
            for value, (_title, width) in zip(values, skill_headers):
                _cell(
                    pdf,
                    width,
                    value,
                    align="L" if width == 52 else "C",
                    fill=fill,
                )
            pdf.ln(7)
        pdf.ln(7)

    headers = [
        ("Course", 48), ("RAG", 20), ("Learners", 20), ("Hours", 18),
        ("Complete", 22), ("Abandon", 22), ("Learning", 20),
        ("Feedback", 28), ("Confidence", 24), ("Pulse", 18),
    ]
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    for title, width in headers:
        _cell(pdf, width, title, bold=True, align="C", fill=True)
    pdf.ln(7)

    if not rows:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 10, "No active courses yet.", ln=True)

    for index, row in enumerate(rows):
        course = row.get("course", {})
        summary_row = row.get("summary", {})
        cohort_state = summary_row.get("cohort_state", "available")
        if cohort_state != "available":
            state_label = (
                "SUPPRESSED" if cohort_state == "suppressed" else "NO EVIDENCE"
            )
            values = [
                f"{course.get('code') or ''} - {course.get('name') or ''}",
                state_label,
                summary_row.get("enrolled_learners", 0),
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
            ]
        else:
            rag = str(summary_row.get("rag") or "none").upper()
            feedback = summary_row.get("reaction_count", 0)
            feedback_text = (
                f"{summary_row.get('positive_rate', 0)}% ({feedback})"
                if feedback else "-"
            )
            confidence = summary_row.get("confidence_gain")
            values = [
                f"{course.get('code') or ''} - {course.get('name') or ''}",
                rag,
                summary_row.get("enrolled_learners", 0),
                summary_row.get("total_learning_hours", 0),
                f"{summary_row.get('completion_rate', 0)}%",
                f"{summary_row.get('abandonment_rate', 0)}%",
                summary_row.get("learning_reported") if summary_row.get("learning_reported") is not None else "-",
                feedback_text,
                f"{confidence:+.1f}" if isinstance(confidence, (int, float)) else "-",
                summary_row.get("pulse_responses", 0),
            ]
        fill = index % 2 == 0
        if fill:
            pdf.set_fill_color(248, 250, 252)
        for value, (_title, width) in zip(values, headers):
            _cell(pdf, width, value, align="C" if width <= 28 else "L", fill=fill)
        pdf.ln(7)

    pdf.ln(4)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(
        0, 5,
        _sanitize_for_pdf(
            "RAG is a teaching signal, not a learner label. Learning is self-reported. "
            "Exercise reactions are optional and shown as totals, never by learner name. "
            "Confidence gain is a performance-growth proxy, not a psychological score. "
            "Courses below the minimum cohort are suppressed rather than shown as zero."
        ),
    )

    return bytes(pdf.output())
