#!/usr/bin/env python3
"""Compute proxy learning metrics from one OpenCyberRange session record.

This is a reference implementation of the metric definitions in
``references/metrics-catalogue.md`` and the event model in
``references/platform-integration.md``. It is deliberately boring: standard
library only, explicit formulas, and warnings when the data cannot support a
metric.

It is not a validated psychometric instrument. Do not use the output to
diagnose, label, rank, or select a person.

Usage:
    python3 compute_session_metrics.py session.json
    python3 compute_session_metrics.py session.json --markdown
    python3 compute_session_metrics.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


METRIC_ORDER = [
    "time_on_task_s",
    "checkpoint_immediate",
    "checkpoint_delayed",
    "retention_index",
    "decision_count",
    "decision_accuracy",
    "decision_latency_median_s",
    "decision_latency_p90_s",
    "throughput_correct_per_min",
    "time_to_first_correct_decision_s",
    "hint_requests",
    "hint_rate_per_decision",
    "interruption_recovery_median_s",
    "reprioritization_alignment",
    "calibration_gap",
    "brier_score",
]


def _events(record: dict[str, Any], event_type: str) -> list[dict[str, Any]]:
    return [e for e in record.get("events", []) if e.get("type") == event_type]


def _checkpoint(record: dict[str, Any], kind: str) -> dict[str, Any] | None:
    for checkpoint in record.get("checkpoints", []):
        if checkpoint.get("kind") == kind:
            return checkpoint
    return None


def _normalised_score(checkpoint: dict[str, Any]) -> float | None:
    score = checkpoint.get("score")
    maximum = checkpoint.get("max", 1.0)
    if score is None or maximum in (None, 0):
        return None
    try:
        return float(score) / float(maximum)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _percentile(values: Iterable[float], fraction: float) -> float | None:
    ordered = sorted(float(v) for v in values)
    if not ordered:
        return None
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def _median(values: Iterable[float]) -> float | None:
    ordered = [float(v) for v in values]
    return statistics.median(ordered) if ordered else None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value in (1, "1", "true", "True", "yes"):
        return True
    if value in (0, "0", "false", "False", "no"):
        return False
    return None


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _time_on_task(record: dict[str, Any]) -> float | None:
    started = _parse_time(record.get("started_at"))
    ended = _parse_time(record.get("ended_at"))
    if started and ended:
        seconds = (ended - started).total_seconds()
        if seconds >= 0:
            return round(seconds, 3)
    timestamps = [
        float(e["t"])
        for e in record.get("events", [])
        if isinstance(e.get("t"), (int, float))
    ]
    if timestamps:
        return round(max(timestamps) - min(timestamps), 3)
    return None


def _decision_latencies(
    record: dict[str, Any], warnings: list[str]
) -> list[float]:
    latencies: list[float] = []
    missing = 0
    for event in _events(record, "decision"):
        value = event.get("latency_s")
        if isinstance(value, (int, float)) and value >= 0:
            latencies.append(float(value))
        else:
            missing += 1
    if missing:
        warnings.append(
            f"{missing} decision event(s) have no numeric latency_s; "
            "they were excluded from latency and throughput metrics."
        )
    return latencies


def _reprioritization_alignment(
    record: dict[str, Any], warnings: list[str]
) -> float | None:
    alignments: list[float] = []
    for event in _events(record, "reprioritize"):
        ranked = list(event.get("ranked") or [])
        expert = list(event.get("expert_ranked") or [])
        if not ranked or not expert:
            warnings.append(
                "A reprioritize event is missing ranked or expert_ranked; "
                "alignment was not computed for it."
            )
            continue
        denominator = min(3, len(ranked), len(expert))
        if denominator < 3:
            warnings.append(
                "A reprioritize event has fewer than three ranked items; "
                f"alignment used the top {denominator}."
            )
        overlap = len(set(ranked[:3]) & set(expert[:3]))
        alignments.append(overlap / denominator)
    return round(statistics.mean(alignments), 4) if alignments else None


def _interruption_recovery(
    record: dict[str, Any], warnings: list[str]
) -> float | None:
    recoveries: list[float] = []
    interruptions = {e.get("interruption_id"): e for e in _events(record, "interruption")}
    for resume in _events(record, "resume"):
        interruption = interruptions.get(resume.get("interruption_id"))
        if not interruption:
            continue
        ends_t = interruption.get("ends_t")
        resume_t = resume.get("t")
        if isinstance(ends_t, (int, float)) and isinstance(resume_t, (int, float)):
            if resume_t >= ends_t:
                recoveries.append(float(resume_t) - float(ends_t))
    if not recoveries:
        if interruptions:
            warnings.append(
                "Interruption recovery could not be calculated; add ends_t to "
                "the interruption and t to the matching resume event."
            )
        return None
    return round(statistics.median(recoveries), 3)


def _calibration(
    record: dict[str, Any], warnings: list[str]
) -> tuple[float | None, float | None]:
    pairs: list[tuple[float, int]] = []
    for event in _events(record, "decision"):
        confidence = event.get("confidence")
        correct = _as_bool(event.get("correct"))
        if confidence is None or correct is None:
            continue
        try:
            confidence_value = float(confidence)
        except (TypeError, ValueError):
            continue
        if not 0 <= confidence_value <= 1:
            warnings.append(
                "A decision confidence value was outside 0-1 and was excluded."
            )
            continue
        pairs.append((confidence_value, 1 if correct else 0))

    if not pairs:
        if _events(record, "decision"):
            warnings.append(
                "Calibration metrics need decision.confidence and "
                "decision.correct; none were complete."
            )
        return None, None

    accuracy = sum(outcome for _, outcome in pairs) / len(pairs)
    mean_confidence = sum(confidence for confidence, _ in pairs) / len(pairs)
    gap = round(mean_confidence - accuracy, 4)
    brier = round(
        sum((confidence - outcome) ** 2 for confidence, outcome in pairs) / len(pairs),
        4,
    )
    return gap, brier


def compute(record: dict[str, Any]) -> dict[str, Any]:
    """Return metrics and warnings for one session record."""
    warnings: list[str] = []

    immediate = _checkpoint(record, "immediate")
    delayed = _checkpoint(record, "delayed")
    immediate_score = _normalised_score(immediate) if immediate else None
    delayed_score = _normalised_score(delayed) if delayed else None

    retention = None
    if immediate_score is not None and delayed_score is not None:
        if immediate_score > 0:
            retention = round(min(delayed_score / immediate_score, 1.0), 4)
        else:
            warnings.append(
                "Retention index is undefined because the immediate checkpoint "
                "score is zero."
            )
    elif delayed is not None:
        warnings.append(
            "Retention index needs both an immediate and a delayed checkpoint."
        )

    decisions = _events(record, "decision")
    correctness = [b for b in (_as_bool(e.get("correct")) for e in decisions) if b is not None]
    decision_accuracy = (
        round(sum(1 for value in correctness if value) / len(correctness), 4)
        if correctness
        else None
    )
    if decisions and len(correctness) != len(decisions):
        warnings.append(
            "Some decision events have no boolean correct field; "
            "decision_accuracy uses only the complete records."
        )

    latencies = _decision_latencies(record, warnings)
    latency_median = round(_median(latencies), 3) if latencies else None
    latency_p90 = round(_percentile(latencies, 0.9), 3) if latencies else None

    throughput = None
    total_latency = sum(latencies)
    if total_latency > 0 and correctness:
        correct_count = sum(1 for value in correctness if value)
        throughput = round(correct_count / (total_latency / 60), 4)

    first_correct = None
    for event in decisions:
        if _as_bool(event.get("correct")) is True:
            latency = event.get("latency_s")
            if isinstance(latency, (int, float)):
                first_correct = round(float(latency), 3)
            elif isinstance(event.get("t"), (int, float)):
                first_correct = round(float(event["t"]), 3)
            break
    if decisions and first_correct is None:
        warnings.append("No correct decision was found for time_to_first_correct_decision_s.")

    hint_count = len(_events(record, "hint_request"))
    hint_rate = round(hint_count / len(decisions), 4) if decisions else None

    recovery = _interruption_recovery(record, warnings)
    alignment = _reprioritization_alignment(record, warnings)
    calibration_gap, brier = _calibration(record, warnings)

    metrics = {
        "time_on_task_s": _time_on_task(record),
        "checkpoint_immediate": (
            round(immediate_score, 4) if immediate_score is not None else None
        ),
        "checkpoint_delayed": (
            round(delayed_score, 4) if delayed_score is not None else None
        ),
        "retention_index": retention,
        "decision_count": len(decisions),
        "decision_accuracy": decision_accuracy,
        "decision_latency_median_s": latency_median,
        "decision_latency_p90_s": latency_p90,
        "throughput_correct_per_min": throughput,
        "time_to_first_correct_decision_s": first_correct,
        "hint_requests": hint_count,
        "hint_rate_per_decision": hint_rate,
        "interruption_recovery_median_s": recovery,
        "reprioritization_alignment": alignment,
        "calibration_gap": calibration_gap,
        "brier_score": brier,
    }

    if not decisions:
        warnings.append("No decision events; speed and calibration metrics are empty.")
    if not _events(record, "reprioritize"):
        warnings.append(
            "No reprioritize event; reprioritisation cannot be measured from "
            "this session alone."
        )

    return {
        "schema_version": "0.1",
        "session_id": record.get("session_id"),
        "learner_id": record.get("learner_id"),
        "lab_slug": record.get("lab_slug"),
        "metrics": metrics,
        "warnings": warnings,
    }


def _format_value(value: Any) -> str:
    if value is None:
        return "not available"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def to_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Session metrics: {result.get('session_id') or 'unknown session'}",
        "",
        f"- Lab: `{result.get('lab_slug') or 'unknown'}`",
        f"- Learner: `{result.get('learner_id') or 'unknown'}`",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for name in METRIC_ORDER:
        lines.append(f"| `{name}` | {_format_value(result['metrics'].get(name))} |")
    lines += [
        "",
        "These are proxies, not diagnoses. Report them with n, spread, the task,",
        "the time limit, the aids allowed, and a limitation.",
    ]
    if result.get("warnings"):
        lines += ["", "## Data warnings", ""]
        lines += [f"- {warning}" for warning in result["warnings"]]
    return "\n".join(lines) + "\n"


def _sample_record() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "session_id": "s-selftest",
        "learner_id": "anon-test",
        "lab_slug": "network-0-1-ping-basics",
        "started_at": "2026-11-01T14:00:00Z",
        "ended_at": "2026-11-01T14:10:00Z",
        "checkpoints": [
            {"kind": "immediate", "score": 8, "max": 10},
            {"kind": "delayed", "score": 6, "max": 10},
        ],
        "events": [
            {"t": 0, "type": "task_start", "task_id": "triage"},
            {"t": 10, "type": "decision", "task_id": "triage", "correct": True, "latency_s": 10, "confidence": 0.9},
            {"t": 22, "type": "decision", "task_id": "triage", "correct": True, "latency_s": 12, "confidence": 0.7},
            {"t": 42, "type": "decision", "task_id": "triage", "correct": False, "latency_s": 20, "confidence": 0.6},
            {"t": 72, "type": "decision", "task_id": "triage", "correct": True, "latency_s": 30, "confidence": 0.8},
            {"t": 80, "type": "hint_request", "hint_id": "h1"},
            {"t": 90, "type": "hint_request", "hint_id": "h2"},
            {"t": 100, "type": "interruption", "interruption_id": "i1", "ends_t": 120},
            {"t": 135, "type": "resume", "interruption_id": "i1", "correct_next_step": True},
            {"t": 150, "type": "change_event", "change_id": "c1", "kind": "new_alert"},
            {"t": 170, "type": "reprioritize", "ranked": ["a", "b", "c"], "expert_ranked": ["b", "a", "d"]},
            {"t": 240, "type": "flag_attempt", "correct": True},
        ],
    }


def _self_test() -> int:
    result = compute(_sample_record())
    got = result["metrics"]
    checks = {
        "time_on_task_s": 600.0,
        "checkpoint_immediate": 0.8,
        "checkpoint_delayed": 0.6,
        "retention_index": 0.75,
        "decision_count": 4,
        "decision_accuracy": 0.75,
        "decision_latency_median_s": 16.0,
        "decision_latency_p90_s": 30.0,
        "throughput_correct_per_min": 2.5,
        "time_to_first_correct_decision_s": 10.0,
        "hint_requests": 2,
        "hint_rate_per_decision": 0.5,
        "interruption_recovery_median_s": 15.0,
        "reprioritization_alignment": 0.6667,
        "calibration_gap": 0.0,
        "brier_score": 0.125,
    }
    failures = []
    for name, expected in checks.items():
        actual = got.get(name)
        if isinstance(expected, float):
            ok = actual is not None and abs(actual - expected) < 0.001
        else:
            ok = actual == expected
        if not ok:
            failures.append(f"{name}: expected {expected!r}, got {actual!r}")

    if failures:
        print("SELF-TEST FAILED", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("SELF-TEST PASSED")
    print(to_markdown(result))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", nargs="?", help="Path to a session JSON record")
    parser.add_argument("--markdown", action="store_true", help="Print a markdown report")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if not args.session:
        parser.error("provide a session JSON path, or use --self-test")

    path = Path(args.session)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(record, dict):
        print("error: session record must be a JSON object", file=sys.stderr)
        return 1

    result = compute(record)
    if args.markdown:
        print(to_markdown(result), end="")
    else:
        print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
