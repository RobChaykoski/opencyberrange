"""Instructor curriculum-demand synthesis.

Turns existing course telemetry into a small set of build recommendations:

* what learners ask for (pulse topic interest);
* where exercises create friction (completion, abandonment, hints, failures);
* which competencies the cohort has little evidence for.

The output is aggregate-only. It never names a learner, and every signal keeps
its sample size so an instructor can judge whether the evidence is strong
enough to act on. It is a planning aid, not an evaluation of teaching.
"""

from __future__ import annotations

from collections import Counter

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# Topic interest keys are broader than track slugs. These hints let the
# service compare demand with the exercises already on offer.
TOPIC_TRACK_HINTS = {
    "web": ("web", "software-security"),
    "osint": ("osint",),
    "forensics": ("forensics",),
    "malware": ("malware",),
    "ot": ("ot", "ics", "scada"),
    "ai": ("ai", "ml"),
    "cloud": ("cloud",),
    "network": ("network",),
    "linux": ("linux",),
    "windows": ("windows",),
    "software-security": ("software-security", "appsec"),
    "career": ("career", "professional"),
    "other": (),
}


def _priority(colour: str) -> str:
    return {"red": "high", "amber": "medium"}.get(colour, "low")


def _supply_for(topic_key: str, exercises: list[dict]) -> int:
    hints = TOPIC_TRACK_HINTS.get(topic_key, ())
    if not hints:
        return 0
    count = 0
    for row in exercises:
        haystack = " ".join(
            str(row.get(field) or "").lower()
            for field in ("track_name", "slug", "lab_name", "chapter_label")
        )
        if any(hint in haystack for hint in hints):
            count += 1
    return count


def _topic_recommendations(topics: list[dict], exercises: list[dict]) -> list[dict]:
    rows = []
    for topic in topics:
        count = int(topic.get("count") or 0)
        if count <= 0:
            continue
        supply = _supply_for(topic["key"], exercises)
        ratio = count / max(1, supply)
        if count >= 8 or ratio >= 4:
            colour = "red"
        elif count >= 3 or ratio >= 2:
            colour = "amber"
        else:
            colour = "green"
        if colour == "green":
            continue
        rows.append(
            {
                "id": f"topic-{topic['key']}",
                "kind": "topic_demand",
                "area": topic["label"],
                "title": f"Build more {topic['label']} exercises",
                "rationale": (
                    f"{count} learner request{'s' if count != 1 else ''} across "
                    f"reporting courses, with {supply} assigned exercise"
                    f"{'s' if supply != 1 else ''} in this area."
                ),
                "evidence": "Pulse topic requests compared with assigned exercises",
                "signal": count,
                "supply": supply,
                "priority": _priority(colour),
                "colour": colour,
                "action": (
                    f"Add one short, guided {topic['label']} exercise and one "
                    "independent variant so learners can choose their pace."
                ),
            }
        )
    rows.sort(key=lambda row: (-row["signal"], row["area"]))
    return rows[:5]


def _friction_recommendations(exercises: list[dict]) -> list[dict]:
    rows = []
    for row in exercises:
        reasons = []
        completion = row.get("completion_rate")
        abandonment = row.get("abandonment_rate")
        hints = row.get("hint_pressure_rate")
        failures = row.get("technical_failure_rate")
        attempts = row.get("median_attempts")

        if completion is not None and completion < 50:
            reasons.append(f"completion {completion}%")
        if abandonment is not None and abandonment >= 40:
            reasons.append(f"abandonment {abandonment}%")
        if hints is not None and hints >= 60:
            reasons.append(f"hint pressure {hints}%")
        if failures is not None and failures >= 20:
            reasons.append(f"technical failures {failures}%")
        if attempts is not None and attempts >= 3:
            reasons.append(f"median {attempts} attempts")

        if not reasons:
            continue

        severe = (
            (completion is not None and completion < 35)
            or (abandonment is not None and abandonment >= 60)
            or (failures is not None and failures >= 35)
        )
        colour = "red" if severe else "amber"
        sample = row.get("sample_size") or 0
        rows.append(
            {
                "id": f"friction-{row.get('lab_id')}",
                "kind": "exercise_friction",
                "area": row.get("track_name") or "Uncategorised",
                "title": f"Rework or scaffold {row.get('lab_name') or 'this exercise'}",
                "rationale": (
                    f"n={sample}; " + ", ".join(reasons) + "."
                ),
                "evidence": "Completion, abandonment, hint, attempt, and failure rates",
                "signal": sample,
                "priority": _priority(colour),
                "colour": colour,
                "course": row.get("course"),
                "action": (
                    "Check the brief and starting state, add a short guided warm-up, "
                    "or split the task into two exercises with a shared evidence step."
                ),
            }
        )
    rows.sort(
        key=lambda row: (
            PRIORITY_RANK.get(row["priority"], 9),
            -(row.get("signal") or 0),
        )
    )
    return rows[:6]


def _competency_recommendations(
    competency: dict, minimum: int
) -> list[dict]:
    if competency.get("state") != "available":
        return []
    cohort_size = int(competency.get("cohort_size") or 0)
    if minimum > 0 and cohort_size < minimum:
        return []

    rows = []
    for domain in competency.get("domains", []):
        gaps = []
        for category in domain.get("categories", []):
            for item in category.get("competencies", []):
                if item.get("state") != "available":
                    continue
                coverage = item.get("coverage_pct")
                if coverage is None or coverage >= 40:
                    continue
                gaps.append(item)
        if not gaps:
            continue
        gaps.sort(key=lambda item: (item.get("coverage_pct") or 0, item["name"]))
        lowest = gaps[:3]
        coverage_values = [item.get("coverage_pct") or 0 for item in gaps]
        colour = "red" if len(gaps) >= 4 else "amber"
        rows.append(
            {
                "id": f"gap-{domain['id']}",
                "kind": "competency_gap",
                "area": domain["label"],
                "title": f"Add practice for {domain['label']}",
                "rationale": (
                    f"{len(gaps)} competencies are below 40% cohort coverage. "
                    f"Lowest: {', '.join(item['name'] for item in lowest)}."
                ),
                "evidence": (
                    f"{cohort_size} learners; coverage ranges "
                    f"{round(min(coverage_values), 1)}-{round(max(coverage_values), 1)}%"
                ),
                "signal": len(gaps),
                "priority": _priority(colour),
                "colour": colour,
                "action": (
                    "Add a beginner exercise for the lowest-coverage competency, "
                    "then a scenario that combines it with an existing strength."
                ),
            }
        )
    rows.sort(
        key=lambda row: (
            PRIORITY_RANK.get(row["priority"], 9),
            -row["signal"],
        )
    )
    return rows[:4]


def build_curriculum_demand(
    *,
    courses: list[dict],
    topics: list[dict],
    exercises: list[dict],
    competency: dict,
    minimum: int,
    generated_at: str,
) -> dict:
    """Synthesize build recommendations from aggregate course telemetry."""
    available_courses = [
        course for course in courses if course.get("cohort_state") == "available"
    ]
    topic_rows = _topic_recommendations(topics, exercises)
    friction_rows = _friction_recommendations(exercises)
    gap_rows = _competency_recommendations(competency, minimum)

    recommendations = topic_rows + friction_rows + gap_rows
    recommendations.sort(
        key=lambda row: (
            PRIORITY_RANK.get(row["priority"], 9),
            -(row.get("signal") or 0),
            row["title"],
        )
    )

    priority_counts = Counter(row["priority"] for row in recommendations)
    kind_counts = Counter(row["kind"] for row in recommendations)

    if not available_courses:
        states = {course.get("cohort_state") for course in courses}
        state = "suppressed" if "suppressed" in states else "no_evidence"
        return {
            "state": state,
            "minimum_cohort_size": minimum,
            "courses_reporting": 0,
            "courses_total": len(courses),
            "topics": [],
            "recommendations": [],
            "summary": {
                "high": 0,
                "medium": 0,
                "low": 0,
                "topic_demand": 0,
                "exercise_friction": 0,
                "competency_gap": 0,
            },
            "reason": (
                "No course has enough learners to report demand without "
                "identifying individuals."
                if state == "suppressed"
                else "No course has telemetry yet."
            ),
            "generated_at": generated_at,
            "disclaimer": _DISCLAIMER,
        }

    return {
        "state": "available",
        "minimum_cohort_size": minimum,
        "courses_reporting": len(available_courses),
        "courses_total": len(courses),
        "cohort_size": competency.get("cohort_size") or 0,
        "topics": topics,
        "recommendations": recommendations,
        "summary": {
            "high": priority_counts.get("high", 0),
            "medium": priority_counts.get("medium", 0),
            "low": priority_counts.get("low", 0),
            "topic_demand": kind_counts.get("topic_demand", 0),
            "exercise_friction": kind_counts.get("exercise_friction", 0),
            "competency_gap": kind_counts.get("competency_gap", 0),
        },
        "generated_at": generated_at,
        "disclaimer": _DISCLAIMER,
    }


_DISCLAIMER = (
    "These are planning prompts from aggregate telemetry, not an evaluation of "
    "teaching or learners. Every recommendation keeps its sample size; treat "
    "small signals as questions to check, not conclusions."
)
