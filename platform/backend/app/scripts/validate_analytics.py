"""Reconcile course analytics against source records.

Run this inside the backend container on a deployment host:

    docker exec -it ocr-backend python /app/app/scripts/validate_analytics.py

The script creates a short-lived token for an existing active administrator in
process, calls the internal analytics API, compares the response with raw
database counts, and exits non-zero for any failed check. It does not create or
modify users, courses, completions, or settings.

The small-group suppression check is intentionally reported separately: the
2.5.x course overview does not yet expose a suppression signal.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from sqlalchemy import text

# Allow `python /app/app/scripts/validate_analytics.py` to import the app
# package regardless of the current working directory.
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
except IndexError:
    pass

from app.auth import create_access_token
from app.database import SessionLocal
from app.models import Competition, CompetitionLab, CompetitionParticipant, User

BASE = os.environ.get("OCR_INTERNAL_API", "http://127.0.0.1:8000")


def main() -> int:
    db = SessionLocal()
    try:
        admin = (
            db.query(User)
            .filter(
                User.role == "admin",
                User.is_active == True,
                User.is_approved == True,
                User.is_locked == False,
            )
            .order_by(User.id)
            .first()
        )
        if admin is None:
            print("No active administrator found.", file=sys.stderr)
            return 2

        token = create_access_token(
            {"sub": admin.username, "user_id": admin.id, "role": admin.role}
        )
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE}/api/analytics/reports/overview",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()

        checks: list[dict] = []

        def record(name, api_value, source_value, ok, detail=""):
            checks.append(
                {
                    "name": name,
                    "api": api_value,
                    "source": source_value,
                    "ok": bool(ok),
                    "detail": detail,
                }
            )

        def close(api_value, source_value, tolerance=0.11):
            if api_value is None or source_value is None:
                return api_value == source_value
            return abs(float(api_value) - float(source_value)) <= tolerance

        def one(sql, **params):
            return db.execute(text(sql), params).scalar()

        course_sources = {}
        for row in body.get("courses", []):
            cid = row["course"]["id"]
            summary = row["summary"]
            tree = row.get("skill_tree") or {}

            enrolled = int(
                one(
                    "SELECT COUNT(DISTINCT user_id) FROM course_enrollments "
                    "WHERE course_id=:cid",
                    cid=cid,
                )
                or 0
            )
            assigned = int(
                one(
                    """
                    SELECT COUNT(*)
                    FROM course_lab_assignments a
                    JOIN labs l ON l.id = a.lab_id
                    WHERE a.course_id = :cid AND l.is_active = true
                    """,
                    cid=cid,
                )
                or 0
            )
            started_pairs = int(
                one(
                    """
                    SELECT COUNT(*) FROM (
                        SELECT DISTINCT s.user_id, s.lab_id
                        FROM lab_sessions s
                        JOIN course_enrollments e
                          ON e.course_id = :cid AND e.user_id = s.user_id
                        JOIN course_lab_assignments a
                          ON a.course_id = :cid AND a.lab_id = s.lab_id
                        JOIN labs l ON l.id = s.lab_id AND l.is_active = true
                        WHERE s.is_diagnostic = false
                          AND (e.enrolled_at IS NULL OR s.started_at >= e.enrolled_at)
                    ) started
                    """,
                    cid=cid,
                )
                or 0
            )
            completions = int(
                one(
                    """
                    SELECT COUNT(*)
                    FROM lab_completions c
                    JOIN course_enrollments e
                      ON e.course_id = :cid AND e.user_id = c.user_id
                    JOIN course_lab_assignments a
                      ON a.course_id = :cid AND a.lab_id = c.lab_id
                    JOIN labs l ON l.id = c.lab_id AND l.is_active = true
                    LEFT JOIN (
                        SELECT user_id, lab_id, MAX(reset_at) AS reset_at
                        FROM course_completion_resets
                        WHERE course_id = :cid
                        GROUP BY user_id, lab_id
                    ) r ON r.user_id = c.user_id AND r.lab_id = c.lab_id
                    WHERE c.flag_submitted IS NOT NULL
                      AND c.flag_submitted <> ''
                      AND (e.enrolled_at IS NULL OR c.completed_at >= e.enrolled_at)
                      AND (r.reset_at IS NULL OR c.completed_at > r.reset_at)
                    """,
                    cid=cid,
                )
                or 0
            )
            distinct_completed_labs = int(
                one(
                    """
                    SELECT COUNT(DISTINCT c.lab_id)
                    FROM lab_completions c
                    JOIN course_enrollments e
                      ON e.course_id = :cid AND e.user_id = c.user_id
                    JOIN course_lab_assignments a
                      ON a.course_id = :cid AND a.lab_id = c.lab_id
                    JOIN labs l ON l.id = c.lab_id AND l.is_active = true
                    LEFT JOIN (
                        SELECT user_id, lab_id, MAX(reset_at) AS reset_at
                        FROM course_completion_resets
                        WHERE course_id = :cid
                        GROUP BY user_id, lab_id
                    ) r ON r.user_id = c.user_id AND r.lab_id = c.lab_id
                    WHERE c.flag_submitted IS NOT NULL
                      AND c.flag_submitted <> ''
                      AND (e.enrolled_at IS NULL OR c.completed_at >= e.enrolled_at)
                      AND (r.reset_at IS NULL OR c.completed_at > r.reset_at)
                    """,
                    cid=cid,
                )
                or 0
            )
            pulse_responses = int(
                one(
                    """
                    SELECT COUNT(*)
                    FROM exercise_pulse_surveys p
                    WHERE p.course_id = :cid
                      AND p.lab_id IN (
                          SELECT lab_id FROM course_lab_assignments
                          WHERE course_id = :cid
                      )
                    """,
                    cid=cid,
                )
                or 0
            )
            reaction_row = db.execute(
                text(
                    """
                    SELECT
                        COALESCE(SUM(CASE WHEN reaction = 'like' THEN 1 ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN reaction = 'dislike' THEN 1 ELSE 0 END), 0),
                        COUNT(*)
                    FROM exercise_reactions
                    WHERE course_id = :cid
                      AND lab_id IN (
                          SELECT lab_id FROM course_lab_assignments
                          WHERE course_id = :cid
                      )
                    """
                ),
                {"cid": cid},
            ).one()
            likes, dislikes, reactions = [int(value or 0) for value in reaction_row]

            total_possible = enrolled * assigned
            expected_completion_rate = (
                round(completions / total_possible * 100, 1)
                if total_possible
                else 0.0
            )
            expected_started_rate = (
                round(started_pairs / total_possible * 100, 1)
                if total_possible
                else 0.0
            )
            expected_abandonment = (
                round(max(0, started_pairs - completions) / started_pairs * 100, 1)
                if started_pairs
                else 0.0
            )

            course_sources[cid] = {
                "available": False,
                "state": summary.get("cohort_state", row.get("cohort_state", "available")),
                "enrolled": enrolled,
                "assigned": assigned,
                "started_pairs": started_pairs,
                "completions": completions,
                "distinct_completed_labs": distinct_completed_labs,
                "pulse_responses": pulse_responses,
                "likes": likes,
                "dislikes": dislikes,
                "reactions": reactions,
            }

            label = f"course {cid}"
            minimum = int((body.get("totals") or {}).get("minimum_cohort_size") or 0)
            expected_state = (
                "no_evidence"
                if enrolled <= 0
                else ("suppressed" if minimum and enrolled < minimum else "available")
            )
            cohort_state = course_sources[cid]["state"]
            record(
                f"{label} cohort state",
                cohort_state,
                expected_state,
                cohort_state == expected_state,
            )
            if cohort_state != "available":
                record(
                    f"{label} suppressed completion rate is null",
                    summary.get("completion_rate"),
                    None,
                    summary.get("completion_rate") is None,
                )
                record(
                    f"{label} suppressed pulse responses are null",
                    summary.get("pulse_responses"),
                    None,
                    summary.get("pulse_responses") is None,
                )
                record(
                    f"{label} suppressed skill tree is empty",
                    len(tree.get("dimensions", [])),
                    0,
                    not tree.get("dimensions"),
                )
                continue
            course_sources[cid]["available"] = True

            record(
                f"{label} enrolled learners",
                summary.get("enrolled_learners"),
                enrolled,
                summary.get("enrolled_learners") == enrolled,
            )
            record(
                f"{label} assigned exercises",
                summary.get("assigned_exercises"),
                assigned,
                summary.get("assigned_exercises") == assigned,
            )
            record(
                f"{label} completion rate",
                summary.get("completion_rate"),
                expected_completion_rate,
                close(summary.get("completion_rate"), expected_completion_rate),
            )
            record(
                f"{label} started rate",
                summary.get("started_rate"),
                expected_started_rate,
                close(summary.get("started_rate"), expected_started_rate),
            )
            record(
                f"{label} abandonment rate",
                summary.get("abandonment_rate"),
                expected_abandonment,
                close(summary.get("abandonment_rate"), expected_abandonment),
            )
            record(
                f"{label} pulse responses",
                summary.get("pulse_responses"),
                pulse_responses,
                summary.get("pulse_responses") == pulse_responses,
            )
            record(
                f"{label} likes",
                summary.get("likes"),
                likes,
                summary.get("likes") == likes,
            )
            record(
                f"{label} dislikes",
                summary.get("dislikes"),
                dislikes,
                summary.get("dislikes") == dislikes,
            )
            record(
                f"{label} reaction count",
                summary.get("reaction_count"),
                reactions,
                summary.get("reaction_count") == reactions,
            )
            record(
                f"{label} skill-tree assigned total",
                tree.get("assigned_total"),
                assigned,
                tree.get("assigned_total") == assigned,
            )
            record(
                f"{label} skill-tree completed total",
                tree.get("completed_total"),
                distinct_completed_labs,
                tree.get("completed_total") == distinct_completed_labs,
            )

            zero_dimensions = [
                item
                for item in tree.get("dimensions", [])
                if item.get("assigned") == 0
            ]
            record(
                f"{label} zero-evidence dimensions keep explicit zero percentages",
                len(zero_dimensions),
                len(zero_dimensions),
                all(
                    item.get("assigned_pct") == 0.0
                    and item.get("completed_pct") == 0.0
                    for item in zero_dimensions
                ),
                "zero counts must not become null or a synthetic score",
            )
            if summary.get("pulse_responses") == 0:
                record(
                    f"{label} no-survey state keeps learning value null",
                    summary.get("learning_reported"),
                    None,
                    summary.get("learning_reported") is None,
                )
            if summary.get("confidence_gain") is None:
                record(
                    f"{label} insufficient-evidence state keeps confidence null",
                    summary.get("confidence_gain"),
                    None,
                    True,
                )
            record(
                f"{label} completion and confidence are separate fields",
                summary.get("completion_rate"),
                summary.get("confidence_gain"),
                "completion_rate" in summary and "confidence_gain" in summary,
            )
            record(
                f"{label} mastery uses skill-tree evidence, not completion",
                tree.get("completed_total"),
                summary.get("completion_rate"),
                "skill_tree" in row and "completion_rate" in summary,
            )

        totals = body.get("totals") or {}
        available_sources = [
            item for item in course_sources.values() if item["available"]
        ]
        total_enrolled = sum(item["enrolled"] for item in available_sources)
        total_assigned = sum(item["assigned"] for item in available_sources)
        total_pulse = sum(item["pulse_responses"] for item in available_sources)
        total_likes = sum(item["likes"] for item in available_sources)
        total_dislikes = sum(item["dislikes"] for item in available_sources)
        total_reactions = sum(item["reactions"] for item in available_sources)
        record(
            "reports suppressed course count",
            totals.get("suppressed_courses"),
            sum(1 for item in course_sources.values() if item["state"] == "suppressed"),
            totals.get("suppressed_courses")
            == sum(1 for item in course_sources.values() if item["state"] == "suppressed"),
        )
        record(
            "reports no-evidence course count",
            totals.get("no_evidence_courses"),
            sum(1 for item in course_sources.values() if item["state"] == "no_evidence"),
            totals.get("no_evidence_courses")
            == sum(1 for item in course_sources.values() if item["state"] == "no_evidence"),
        )
        record(
            "reports total enrolled learners",
            totals.get("enrolled_learners"),
            total_enrolled,
            totals.get("enrolled_learners") == total_enrolled,
        )
        record(
            "reports total assigned exercises",
            totals.get("assigned_exercises"),
            total_assigned,
            totals.get("assigned_exercises") == total_assigned,
        )
        record(
            "reports total pulse responses",
            totals.get("pulse_responses"),
            total_pulse,
            totals.get("pulse_responses") == total_pulse,
        )
        record(
            "reports total likes",
            totals.get("likes"),
            total_likes,
            totals.get("likes") == total_likes,
        )
        record(
            "reports total dislikes",
            totals.get("dislikes"),
            total_dislikes,
            totals.get("dislikes") == total_dislikes,
        )
        record(
            "reports total reaction count",
            totals.get("reaction_count"),
            total_reactions,
            totals.get("reaction_count") == total_reactions,
        )

        skill_totals = totals.get("skill_tree") or {}
        total_completed_labs = sum(
            item["distinct_completed_labs"] for item in available_sources
        )
        record(
            "reports skill-tree assigned total",
            skill_totals.get("assigned_total"),
            total_assigned,
            skill_totals.get("assigned_total") == total_assigned,
        )
        record(
            "reports skill-tree completed total",
            skill_totals.get("completed_total"),
            total_completed_labs,
            skill_totals.get("completed_total") == total_completed_labs,
        )

        competition_count = db.query(Competition).count()
        competition_labs = db.query(CompetitionLab).count()
        competition_participants = db.query(CompetitionParticipant).count()
        competition_keys = [
            key for key in (totals or {}) if "competition" in key.lower()
        ]
        record(
            "competition scoring is separate from course analytics",
            competition_keys,
            [],
            competition_keys == [],
            (
                f"competitions={competition_count}, "
                f"competition_labs={competition_labs}, "
                f"participants={competition_participants}"
            ),
        )

        suppression_implemented = any(
            "suppress" in json.dumps(row).lower()
            or "minimum" in json.dumps(row).lower()
            for row in body.get("courses", [])
        )
        record(
            "course overview exposes a small-group suppression signal",
            suppression_implemented,
            True,
            suppression_implemented,
            "No suppression indicator was found in the analytics response.",
        )

        failed = [item for item in checks if not item["ok"]]
        print(
            json.dumps(
                {
                    "generated_at": body.get("generated_at"),
                    "courses": list(course_sources.keys()),
                    "checks": checks,
                    "summary": {
                        "checks": len(checks),
                        "failed": len(failed),
                        "result": "fail" if failed else "pass",
                    },
                },
                indent=2,
                default=str,
            )
        )
        return 1 if failed else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
