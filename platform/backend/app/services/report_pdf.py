"""Narrative PDF reports for instructors.

These reports are decision aids, not record dumps. The existing student record
pack remains available separately; the class-level reports use aggregates,
denominators, and the platform's minimum-cohort suppression rules.
"""

from __future__ import annotations

from datetime import datetime

from fpdf import FPDF

from app.services.pdf_report import _configure_pdf, _sanitize_for_pdf


def _pct(value, n=None) -> str:
    if value is None:
        return "—"
    text = f"{float(value):.1f}%"
    if n is not None:
        text += f" (n={n})"
    return text


def _number(value, suffix: str = "") -> str:
    if value is None:
        return "—"
    return f"{value}{suffix}"


def _clip(text: str, width: float, font_size: float) -> str:
    max_chars = max(4, int(width / (font_size * 0.20)))
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


class ReportPDF(FPDF):
    def __init__(
        self,
        course_label: str,
        report_title: str,
        orientation: str = "P",
        report_id: str = "",
    ):
        super().__init__(orientation=orientation, unit="mm", format="A4")
        self.course_label = course_label
        self.report_title = report_title
        self.report_id = report_id
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(12, 12, 12)

    def header(self):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            5,
            _sanitize_for_pdf(f"{self.course_label} | {self.report_title}"),
            align="R",
        )
        self.ln(6)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(120, 120, 120)
        identifier = f"Report {self.report_id} | " if self.report_id else ""
        self.cell(
            0,
            5,
            _sanitize_for_pdf(
                f"{identifier}SWOCTS Cyber Range | Page {self.page_no()}"
            ),
            align="C",
        )


def _heading(pdf: FPDF, text: str, size: float = 14) -> None:
    pdf.set_font("Helvetica", "B", size)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(0, 7, _sanitize_for_pdf(text))
    pdf.ln(2)


def _body(pdf: FPDF, text: str, size: float = 10) -> None:
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 5, _sanitize_for_pdf(text))
    pdf.ln(1)


def _bullets(pdf: FPDF, items: list[str], size: float = 9.5) -> None:
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(51, 65, 85)
    for item in items:
        pdf.multi_cell(0, 5, _sanitize_for_pdf(f"- {item}"))
    pdf.ln(1)


def _table(
    pdf: FPDF,
    headers: list[str],
    widths: list[float],
    rows: list[list],
    *,
    font_size: float = 8,
    line_height: float = 5,
) -> None:
    def draw_header() -> None:
        pdf.set_font("Helvetica", "B", font_size)
        pdf.set_fill_color(226, 232, 240)
        pdf.set_text_color(30, 41, 59)
        for header, width in zip(headers, widths, strict=False):
            pdf.cell(width, line_height + 1, _sanitize_for_pdf(header), border=1, fill=True)
        pdf.ln(line_height + 1)

    draw_header()
    pdf.set_font("Helvetica", "", font_size)
    pdf.set_text_color(51, 65, 85)
    for row in rows:
        if pdf.get_y() > pdf.h - 20:
            pdf.add_page()
            draw_header()
            pdf.set_font("Helvetica", "", font_size)
            pdf.set_text_color(51, 65, 85)
        for value, width in zip(row, widths, strict=False):
            text = _sanitize_for_pdf("" if value is None else str(value))
            pdf.cell(width, line_height, _clip(text, width, font_size), border=1)
        pdf.ln(line_height)


def _limitations(pdf: FPDF) -> None:
    _heading(pdf, "What this report can and cannot tell you", 11)
    _bullets(
        pdf,
        [
            "Percentages use the stated denominator. Enrolled learners and assigned exercises are the default course denominator.",
            "Pulse and survey responses are optional. Respondents may differ from non-respondents.",
            "Completion can exist without a matching session on some deployments, so start rates may understate activity.",
            "Cohorts below the configured minimum are suppressed rather than reported as zero.",
            "RAG is a teaching signal, not a learner label or a prediction.",
            "Very fast, hint-free completions may reflect prior knowledge, accessibility needs, outside help, or low interest. Use them to start a supportive conversation, never as punishment or proof of AI use.",
        ],
        9,
    )


def generate_course_health_pdf(
    overview: dict,
    exercises_payload: dict,
    generated_at: datetime,
    report_id: str = "",
) -> bytes:
    course = overview.get("course") or {}
    summary = overview.get("summary") or {}
    label = f"{course.get('code', '')} - {course.get('name', '')}".strip(" -")
    pdf = ReportPDF(label, "Course health brief", report_id=report_id)
    _configure_pdf(pdf, f"{label} course health brief", "Course health brief")
    pdf.add_page()

    _heading(pdf, "Course health brief")
    _body(
        pdf,
        f"Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')}. "
        "This brief is for a teaching decision, not a learner ranking.",
        9,
    )

    cohort_state = str(overview.get("cohort_state") or "available")
    if cohort_state != "available":
        _heading(pdf, "Cohort evidence", 11)
        suppression = overview.get("suppression") or {}
        _body(
            pdf,
            suppression.get("reason")
            or "There is not enough cohort evidence to report this course yet.",
        )
    else:
        _heading(pdf, "At a glance", 11)
        rows = [
            ("Enrolled learners", summary.get("enrolled_learners", 0)),
            ("Assigned exercises", summary.get("assigned_exercises", 0)),
            ("Started learners", summary.get("started_learners", 0)),
            ("Completed learners", summary.get("completed_learners", 0)),
            (
                "Exercise completion",
                _pct(summary.get("completion_rate"), summary.get("assigned_exercises")),
            ),
            ("Started exercise pairs", _pct(summary.get("started_rate"))),
            ("Abandonment", _pct(summary.get("abandonment_rate"))),
            ("Median time per completion", _number(summary.get("median_time_minutes"), " min")),
            ("Median attempts", _number(summary.get("median_attempts"))),
            ("Hint-free completions", _pct(summary.get("hint_free_rate"))),
            ("First-attempt success", _pct(summary.get("first_attempt_rate"))),
            (
                "Pulse responses",
                f"{summary.get('pulse_responses', 0)} "
                f"(learning {summary.get('learning_reported') if summary.get('learning_reported') is not None else '—'})",
            ),
            ("Teaching status", str(summary.get("rag") or "unknown").upper()),
        ]
        for label_text, value in rows:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(51, 65, 85)
            pdf.cell(70, 6, _sanitize_for_pdf(label_text), border=0)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 6, _sanitize_for_pdf(str(value)), border=0)
            pdf.ln(6)

        reasons = summary.get("rag_reasons") or []
        if reasons:
            pdf.ln(2)
            _heading(pdf, "Why this status", 11)
            _bullets(pdf, [str(reason) for reason in reasons], 9)

    exercises = exercises_payload.get("exercises") or []
    watch = [
        row
        for row in exercises
        if row.get("flags") or str(row.get("rag") or "").lower() in {"red", "amber"}
    ]
    watch.sort(key=lambda row: (row.get("completion_rate") or 0, row.get("lab_name") or ""))
    watch = watch[:6]
    if watch:
        _heading(pdf, "Exercise watchlist", 11)
        table_rows = []
        for row in watch:
            table_rows.append(
                [
                    row.get("lab_name") or "Unnamed",
                    row.get("sample_size") or 0,
                    _pct(row.get("completion_rate"), row.get("sample_size")),
                    _pct(row.get("hint_pressure_rate")),
                    _number(row.get("median_attempts")),
                    str(row.get("rag") or "—").upper(),
                    ", ".join(row.get("flags") or []) or "—",
                ]
            )
        _table(
            pdf,
            ["Exercise", "n", "Completion", "Hints", "Attempts", "RAG", "Flags"],
            [55, 10, 30, 24, 18, 15, 34],
            table_rows,
            font_size=7.5,
            line_height=5,
        )
        pdf.ln(2)

    _heading(pdf, "One next step for the teaching team", 11)
    actions = []
    text_reasons = " ".join(str(reason).lower() for reason in (summary.get("rag_reasons") or []))
    if "low completion" in text_reasons:
        actions.append("Pick the lowest-completion exercise and review its prerequisites, hints, and workbook before adding more work.")
    if "attempt" in text_reasons:
        actions.append("Add one worked example or a smaller checkpoint to the exercise with the highest attempt burden.")
    if "hint" in text_reasons:
        actions.append("Review the exercise with the highest hint pressure for a missing concept or unclear instruction.")
    if "learning" in text_reasons or "difficulty" in text_reasons:
        actions.append("Run a short clarity check on the exercise learners rate as difficult or low-learning.")
    if not actions:
        actions.append("Continue the current plan and re-check the same measures after the next teaching cycle.")
    _bullets(pdf, actions[:3], 9.5)

    _limitations(pdf)
    return bytes(pdf.output())


def generate_exercise_diagnostics_pdf(
    exercises_payload: dict,
    generated_at: datetime,
    report_id: str = "",
) -> bytes:
    course = exercises_payload.get("course") or {}
    label = f"{course.get('code', '')} - {course.get('name', '')}".strip(" -")
    pdf = ReportPDF(
        label, "Exercise diagnostics", orientation="L", report_id=report_id
    )
    _configure_pdf(pdf, f"{label} exercise diagnostics", "Exercise diagnostics")
    pdf.add_page()

    _heading(pdf, "Exercise diagnostics")
    _body(
        pdf,
        f"Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')}. "
        "Use this report to find content and scaffolding problems and to compare "
        "solve time and hint use with the cohort baseline, not to rank learners.",
        9,
    )

    cohort_state = str(exercises_payload.get("cohort_state") or "available")
    if cohort_state != "available":
        suppression = exercises_payload.get("suppression") or {}
        _body(
            pdf,
            suppression.get("reason")
            or "There is not enough cohort evidence to report exercise diagnostics yet.",
        )
        _limitations(pdf)
        return bytes(pdf.output())

    rows = []
    for row in exercises_payload.get("exercises") or []:
        flags = ", ".join(row.get("flags") or []) or "—"
        rows.append(
            [
                row.get("lab_name") or "Unnamed",
                f"{row.get('track_name') or 'Uncategorized'} / {row.get('level_name') or '—'}",
                row.get("sample_size") or 0,
                row.get("started_learners") or 0,
                row.get("completed_learners") or 0,
                _pct(row.get("completion_rate")),
                _pct(row.get("abandonment_rate")),
                _number(row.get("median_time_minutes"), " min"),
                _number(row.get("baseline_mean_time_minutes"), " min"),
                _number(row.get("median_attempts")),
                _number(row.get("baseline_median_hints")),
                _number(row.get("baseline_mean_hints")),
                str(row.get("rag") or "—").upper(),
                flags,
            ]
        )

    if not rows:
        _body(pdf, "No exercises are assigned to this course yet.")
    else:
        _table(
            pdf,
            [
                "Exercise",
                "Track / level",
                "n",
                "Started",
                "Completed",
                "Completion",
                "Abandon",
                "Median time",
                "Mean time",
                "Attempts",
                "Median hints",
                "Mean hints",
                "RAG",
                "Flags",
            ],
            [48, 34, 8, 12, 14, 16, 15, 18, 18, 13, 12, 14, 11, 40],
            rows,
            font_size=6.8,
            line_height=4.4,
        )
    _limitations(pdf)
    return bytes(pdf.output())


def generate_coaching_queue_pdf(
    course: dict,
    rows: list[dict],
    generated_at: datetime,
    report_id: str = "",
) -> bytes:
    label = f"{course.get('code', '')} - {course.get('name', '')}".strip(" -")
    pdf = ReportPDF(
        label, "Coaching queue", orientation="L", report_id=report_id
    )
    _configure_pdf(pdf, f"{label} coaching queue", "Coaching queue")
    pdf.add_page()

    _heading(pdf, "Coaching queue")
    _body(
        pdf,
        f"Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')}. "
        "This is a teaching queue, not a ranking. Each row has one suggested next step and a review date.",
        9,
    )

    if not rows:
        _body(pdf, "No learners met the coaching-queue criteria in this window.")
    else:
        table_rows = [
            [
                row.get("learner"),
                row.get("signal"),
                row.get("evidence"),
                row.get("suggested_action"),
                row.get("review_date"),
            ]
            for row in rows
        ]
        _table(
            pdf,
            ["Learner", "Signal", "Evidence", "Suggested next step", "Review"],
            [38, 55, 90, 75, 22],
            table_rows,
            font_size=7.2,
            line_height=4.8,
        )
    _body(
        pdf,
        "Signals are descriptive and based on the recorded activity. Check access, schedule, and data quality before treating a signal as a learning problem.",
        8.5,
    )
    return bytes(pdf.output())
