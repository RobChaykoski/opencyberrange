"""Build individual and cohort competency radar payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import median, quantiles

from sqlalchemy.orm import joinedload

from app.models import (
    CourseEnrollment,
    CourseFeedback,
    ExercisePulseSurvey,
    ExerciseQuizAttempt,
    Lab,
    LabCompletion,
    Level,
)
from app.services.competency_model import (
    AXES,
    AXIS_KEYS,
    COMPETENCY_MODEL_VERSION,
    SCORE_WEIGHTS,
    TARGET_SCORE,
    mapping_for_lab,
    parse_mapping,
)


def _utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value):
    value = _utc(value)
    return value.isoformat() if value else None


def _avg(values):
    clean = [value for value in values if value is not None]
    return round(sum(clean) / len(clean), 1) if clean else None


def _rate(part, total):
    return round(part / total * 100, 1) if total else None


def _quality(sample_size: int, coverage: float) -> str:
    if sample_size <= 0:
        return "insufficient"
    if sample_size >= 5 and coverage >= 90:
        return "strong"
    if sample_size >= 3 and coverage >= 70:
        return "growing"
    return "early"


def _component_status(value):
    if value is None:
        return "grey"
    if value >= 80:
        return "green"
    if value >= 60:
        return "amber"
    return "red"


def _completion_rows(db, user_id):
    return (
        db.query(LabCompletion)
        .options(joinedload(LabCompletion.lab).joinedload(Lab.level).joinedload(Level.track))
        .filter(
            LabCompletion.user_id == user_id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .all()
    )


def _quiz_rows(db, user_id):
    return (
        db.query(ExerciseQuizAttempt)
        .options(joinedload(ExerciseQuizAttempt.lab).joinedload(Lab.level).joinedload(Level.track))
        .filter(ExerciseQuizAttempt.user_id == user_id)
        .all()
    )


def _feedback_rows(db, user_id):
    return db.query(CourseFeedback).filter(
        CourseFeedback.subject_user_id == user_id,
        CourseFeedback.direction == "instructor_student",
    ).all()


def _pulse_rows(db, user_id):
    return db.query(ExercisePulseSurvey).filter(
        ExercisePulseSurvey.user_id == user_id
    ).all()


def _axis_entries(axis_key, completions):
    entries = []
    for completion in completions:
        mapping = parse_mapping(completion.competency_mapping, completion.lab)
        weight = float(mapping.get("weights", {}).get(axis_key, 0) or 0)
        if weight <= 0 or completion.lab is None:
            continue
        level = completion.lab.level.level_number if completion.lab.level else 0
        entries.append({
            "completion": completion,
            "weight": weight,
            "mapping": mapping,
            "level": level,
        })
    return entries


def _axis_assessments(axis_key, quizzes):
    rows = []
    for quiz in quizzes:
        if quiz.lab is None:
            continue
        mapping = mapping_for_lab(quiz.lab)
        if float(mapping.get("weights", {}).get(axis_key, 0) or 0) > 0:
            rows.append(quiz)
    return rows


def _independent_score(entries):
    if not entries:
        return None
    independent = sum(
        1 for entry in entries
        if (entry["completion"].hints_used or 0) == 0
        and (entry["completion"].attempts or 0) <= 1
    )
    return _rate(independent, len(entries))


def _retained_score(entries):
    if len(entries) < 2:
        return None
    min_level = min(entry["level"] for entry in entries)
    later = [entry for entry in entries if entry["level"] >= min_level + 2]
    if len(later) < 2:
        return None
    return _independent_score(later)


def _score(entries, assessments, feedback, *, include_assessment=True, include_feedback=True):
    independent = _independent_score(entries)
    assessment = (
        _avg([quiz.score for quiz in assessments])
        if include_assessment and assessments else None
    )
    retained = _retained_score(entries)
    instructor = None
    if include_feedback and feedback and entries:
        ratings = []
        for row in feedback:
            ratings.extend(
                value for value in (row.clarity, row.challenge, row.engagement, row.confidence)
                if value is not None
            )
        if ratings:
            instructor = round((sum(ratings) / len(ratings)) * 20, 1)

    components = {
        "assessment": assessment,
        "independent": independent,
        "retained": retained,
        "instructor": instructor,
    }
    available_weight = sum(
        weight for name, weight in SCORE_WEIGHTS.items()
        if components[name] is not None
    )
    weighted = sum(
        (components[name] or 0) * weight
        for name, weight in SCORE_WEIGHTS.items()
        if components[name] is not None
    )
    coverage = round(available_weight * 100, 1)
    provisional = round(weighted / available_weight, 1) if available_weight else None
    return {
        "components": components,
        "component_status": {
            name: _component_status(value) for name, value in components.items()
        },
        "score": round(weighted, 1) if available_weight else None,
        "provisional_score": provisional,
        "weight_coverage_pct": coverage,
        "provisional": available_weight < sum(SCORE_WEIGHTS.values()),
        "evidence_quality": _quality(len(entries) + len(assessments) + len(feedback), coverage),
    }


def _axis_payload(axis, entries, assessments, feedback, pulse):
    latest_candidates = []
    for entry in entries:
        latest_candidates.append(_utc(entry["completion"].completed_at))
    latest_candidates.extend(_utc(quiz.taken_at) for quiz in assessments)
    latest_candidates.extend(_utc(row.created_at) for row in feedback)
    latest = max((value for value in latest_candidates if value), default=None)

    baseline_entries = sorted(
        entries, key=lambda entry: _utc(entry["completion"].completed_at) or datetime.min.replace(tzinfo=timezone.utc)
    )
    baseline_count = max(1, int(len(baseline_entries) * 0.3)) if baseline_entries else 0
    baseline = _score(baseline_entries[:baseline_count], [], [], include_assessment=False, include_feedback=False)
    current = _score(entries, assessments, feedback)

    mapping_versions = sorted({
        str(entry["mapping"].get("mapping_version") or entry["mapping"].get("model_version"))
        for entry in entries
    })
    drilldown_labs = [
        {
            "lab_id": entry["completion"].lab_id,
            "lab_name": entry["completion"].lab.name if entry["completion"].lab else None,
            "track": (
                entry["completion"].lab.level.track.name
                if entry["completion"].lab and entry["completion"].lab.level
                and entry["completion"].lab.level.track else None
            ),
            "completed_at": _iso(entry["completion"].completed_at),
            "weight": entry["weight"],
            "mapping_version": entry["mapping"].get("mapping_version"),
            "difficulty": entry["mapping"].get("difficulty"),
        }
        for entry in sorted(
            entries,
            key=lambda entry: _utc(entry["completion"].completed_at) or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
    ]
    drilldown_assessments = [
        {
            "lab_id": quiz.lab_id,
            "lab_name": quiz.lab.name if quiz.lab else None,
            "score": quiz.score,
            "taken_at": _iso(quiz.taken_at),
        }
        for quiz in assessments
    ]
    pulse_learning = _avg([row.learning for row in pulse])
    return {
        **axis,
        "baseline": baseline["provisional_score"],
        "current": current["provisional_score"],
        "target": TARGET_SCORE,
        "score": current["score"],
        "provisional": current["provisional"],
        "weight_coverage_pct": current["weight_coverage_pct"],
        "evidence_quality": current["evidence_quality"],
        "components": current["components"],
        "component_status": current["component_status"],
        "sample_size": len(entries) + len(assessments) + len(feedback),
        "evidence_count": len(entries) + len(assessments) + len(feedback),
        "latest_evidence_at": _iso(latest),
        "recency_days": (
            round((datetime.now(timezone.utc) - latest).total_seconds() / 86400, 1)
            if latest else None
        ),
        "model_version": COMPETENCY_MODEL_VERSION,
        "mapping_versions": mapping_versions,
        "sources": {
            "observed": len(entries) + len(assessments),
            "self_reported": len(pulse),
            "instructor": len(feedback),
        },
        "self_confidence": {
            "value": round(pulse_learning * 20, 1) if pulse_learning is not None else None,
            "responses": len(pulse),
            "label": "Self-reported learning, not included in the score",
        },
        "contributing_labs": drilldown_labs,
        "contributing_assessments": drilldown_assessments,
    }


def build_individual_radar(db, user_id: int) -> dict:
    completions = _completion_rows(db, user_id)
    quizzes = _quiz_rows(db, user_id)
    feedback = _feedback_rows(db, user_id)
    pulse = _pulse_rows(db, user_id)

    axes = []
    for axis in AXES:
        key = axis["key"]
        entries = _axis_entries(key, completions)
        assessments = _axis_assessments(key, quizzes)
        axis_pulse = [
            row for row in pulse
            if row.lab_id in {entry["completion"].lab_id for entry in entries}
        ]
        axes.append(_axis_payload(axis, entries, assessments, feedback, axis_pulse))

    scored = [axis["current"] for axis in axes if axis["current"] is not None]
    return {
        "mode": "individual",
        "model_version": COMPETENCY_MODEL_VERSION,
        "mapping_version": COMPETENCY_MODEL_VERSION,
        "target_profile": TARGET_SCORE,
        "weights": SCORE_WEIGHTS,
        "axes": axes,
        "overall": round(sum(scored) / len(scored), 1) if scored else None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": [
            "Scores use 50% assessment, 25% independent completion, 15% retained/transfer, and 10% instructor evidence.",
            "Missing components are shown as provisional with weight coverage, not silently redistributed.",
            "Self-confidence is separate from the competency score.",
        ],
    }


def build_cohort_radar(db, course, learner_ids, minimum: int) -> dict:
    learner_ids = list(learner_ids)[:300]
    individual = [build_individual_radar(db, user_id) for user_id in learner_ids]
    axes = []
    for index, axis in enumerate(AXES):
        values = []
        component_values = {name: [] for name in SCORE_WEIGHTS}
        labs = {}
        assessments = {}
        mapping_versions = set()
        for radar in individual:
            row = radar["axes"][index]
            if row["current"] is not None:
                values.append(row["current"])
            for name, value in row["components"].items():
                if value is not None:
                    component_values[name].append(value)
            for lab in row["contributing_labs"]:
                labs[lab["lab_id"]] = lab
            for assessment in row["contributing_assessments"]:
                assessments[assessment["lab_id"]] = assessment
            mapping_versions.update(row["mapping_versions"])
        suppressed = len(values) < minimum
        q1 = q3 = None
        med = None
        if not suppressed and values:
            med = round(float(median(values)), 1)
            if len(values) >= 4:
                q1_value, _q2, q3_value = quantiles(values, n=4, method="inclusive")
                q1, q3 = round(q1_value, 1), round(q3_value, 1)
            else:
                q1 = q3 = med
        axes.append({
            **axis,
            "cohort_median": None if suppressed else med,
            "cohort_q1": None if suppressed else q1,
            "cohort_q3": None if suppressed else q3,
            "target": TARGET_SCORE,
            "learners_with_evidence": len(values),
            "sample_size": len(values),
            "suppressed": suppressed,
            "components_median": {
                name: _avg(values) for name, values in component_values.items()
            },
            "mapping_versions": sorted(mapping_versions),
            "contributing_labs": list(labs.values())[:50],
            "contributing_assessments": list(assessments.values())[:50],
        })
    return {
        "mode": "cohort",
        "course": {"id": course.id, "code": course.code, "name": course.name},
        "model_version": COMPETENCY_MODEL_VERSION,
        "mapping_version": COMPETENCY_MODEL_VERSION,
        "target_profile": TARGET_SCORE,
        "minimum_cohort_size": minimum,
        "learners_with_evidence": sum(1 for radar in individual if radar["overall"] is not None),
        "suppressed": all(axis["suppressed"] for axis in axes),
        "axes": axes,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": [
            "Cohort medians and interquartile bands are suppressed below the minimum cohort size.",
            "Only learners with evidence contribute to a cohort axis.",
        ],
    }
