"""Optional exercise knowledge checks.

Question banks live in ``quiz.yaml`` beside each lab. They are benchmark-style
practice, not exam items. A learner may re-attempt as often as they like; each
attempt draws a small random sample from the bank. Correct answers and
explanations are revealed after submission.

The bank stays in YAML so adding a question is a content change, not a schema
change. Attempts store the selected question ids and answers so old results
remain reproducible when the bank grows.
"""

from __future__ import annotations

import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
from sqlalchemy.orm import Session

from app.models import (
    CourseEnrollment,
    CourseLabAssignment,
    ExerciseQuizAttempt,
    ExerciseQuizFeedback,
    Lab,
    LabCompletion,
    User,
)
from app.services.achievements import check_quiz_achievements
from app.services import certification_quiz

LABS_ROOT = Path(os.environ.get("LABS_DIR", "/labs"))
PASSING_SCORE = 70
_LAB_DIRS: dict[str, Path] | None = None
_QUIZ_CACHE: dict[str, tuple[float, dict]] = {}


def reset_cache():
    """Clear the in-process cache (used by tests and after a content update)."""
    global _LAB_DIRS
    _LAB_DIRS = None
    _QUIZ_CACHE.clear()


def _lab_dirs() -> dict[str, Path]:
    global _LAB_DIRS
    if _LAB_DIRS is None:
        mapping: dict[str, Path] = {}
        if LABS_ROOT.exists():
            for lab_yaml in LABS_ROOT.rglob("lab.yaml"):
                parent = lab_yaml.parent
                mapping[parent.name] = parent
        _LAB_DIRS = mapping
    return _LAB_DIRS


def quiz_path(lab_slug: str) -> Optional[Path]:
    lab_dir = _lab_dirs().get(lab_slug)
    if not lab_dir:
        return None
    for name in ("quiz.yaml", "quiz.yml", "quiz.json"):
        candidate = lab_dir / name
        if candidate.exists():
            return candidate
    return None


def track_quiz_path(lab_slug: str) -> Optional[Path]:
    lab_dir = _lab_dirs().get(lab_slug)
    if not lab_dir:
        return None
    for name in ("_track_quiz.yaml", "_track_quiz.yml", "_track_quiz.json"):
        candidate = lab_dir.parent / name
        if candidate.exists():
            return candidate
    return None


def quiz_available(lab_slug: str) -> bool:
    return quiz_path(lab_slug) is not None or track_quiz_path(lab_slug) is not None


def _normalize_quiz(raw: dict, path: Path, source: str = "lab") -> dict:
    if not isinstance(raw, dict):
        raise ValueError("quiz file must contain a mapping")
    cert = raw.get("certification") or {}
    questions = []
    seen = set()
    for index, item in enumerate(raw.get("questions") or []):
        if not isinstance(item, dict):
            raise ValueError(f"question {index + 1} must be a mapping")
        question_id = str(item.get("id") or f"q{index + 1}").strip()
        if not question_id or question_id in seen:
            raise ValueError(f"question {index + 1} needs a unique id")
        seen.add(question_id)
        options = [str(option).strip() for option in (item.get("options") or [])]
        if len(options) < 2:
            raise ValueError(f"question {question_id} needs at least two options")
        correct = item.get("correct")
        if not isinstance(correct, int) or not 0 <= correct < len(options):
            raise ValueError(f"question {question_id} has an invalid correct index")
        explanation = str(item.get("explanation") or "").strip()
        if not explanation:
            raise ValueError(f"question {question_id} needs an explanation")
        reference = item.get("reference") or {}
        questions.append({
            "id": question_id,
            "prompt": str(item.get("prompt") or "").strip(),
            "options": options,
            "correct": correct,
            "explanation": explanation,
            "reference": {
                "label": str(reference.get("label") or "").strip(),
                "url": str(reference.get("url") or "").strip(),
            },
            "difficulty": str(item.get("difficulty") or "benchmark").strip(),
        })
    if len(questions) < 2:
        raise ValueError("a quiz needs at least two questions")
    return {
        "source": source,
        "certification": {
            "name": str(cert.get("name") or "General benchmark").strip(),
            "code": str(cert.get("code") or "").strip(),
            "url": str(cert.get("url") or "").strip(),
            "scope": str(
                cert.get("scope")
                or "Benchmark practice only; these are not actual exam questions."
            ).strip(),
        },
        "questions": questions,
        "path": str(path),
    }


def load_quiz(lab_slug: str) -> Optional[dict]:
    path = quiz_path(lab_slug)
    source = "lab"
    if not path:
        path = track_quiz_path(lab_slug)
        source = "track"
    if not path:
        return None
    try:
        mtime = path.stat().st_mtime
        cached = _QUIZ_CACHE.get(lab_slug)
        if cached and cached[0] == mtime:
            return cached[1]
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        normalized = _normalize_quiz(raw, path, source)
        _QUIZ_CACHE[lab_slug] = (mtime, normalized)
        return normalized
    except Exception:
        return None


def question_sample_count(quiz: dict) -> int:
    # Keep the check short: a track fallback uses two questions; a dedicated
    # certification bank uses three from its five-to-six question pool.
    if quiz.get("source") == "track" or len(quiz["questions"]) <= 3:
        return 2
    return 3


def _previous_keys(db: Session, user_id: int, lab_id: int) -> set[str]:
    row = (
        db.query(ExerciseQuizAttempt)
        .filter(
            ExerciseQuizAttempt.user_id == user_id,
            ExerciseQuizAttempt.lab_id == lab_id,
        )
        .order_by(ExerciseQuizAttempt.id.desc())
        .first()
    )
    if not row:
        return set()
    try:
        return set(json.loads(row.question_keys or "[]"))
    except (TypeError, ValueError):
        return set()


def sample_questions(quiz: dict, previous_keys: set[str], count: int) -> list[dict]:
    questions = quiz["questions"]
    pool = [question for question in questions if question["id"] not in previous_keys]
    if len(pool) < count:
        pool = questions
    return random.sample(pool, min(count, len(pool)))


def course_id_for_lab(db: Session, user_id: int, lab_id: int) -> Optional[int]:
    row = (
        db.query(CourseLabAssignment.course_id)
        .join(
            CourseEnrollment,
            CourseEnrollment.course_id == CourseLabAssignment.course_id,
        )
        .filter(
            CourseEnrollment.user_id == user_id,
            CourseLabAssignment.lab_id == lab_id,
        )
        .first()
    )
    return row[0] if row else None


def _best_scores(db: Session, user_id: int, lab_id: int) -> list[int]:
    rows = (
        db.query(ExerciseQuizAttempt.score)
        .filter(
            ExerciseQuizAttempt.user_id == user_id,
            ExerciseQuizAttempt.lab_id == lab_id,
            ExerciseQuizAttempt.completed_at.isnot(None),
        )
        .all()
    )
    return [row[0] or 0 for row in rows]


def _feedback_payload(row: ExerciseQuizFeedback | None) -> Optional[dict]:
    if row is None:
        return None
    return {
        "satisfaction": row.satisfaction,
        "relevance": row.relevance,
        "usefulness": row.usefulness,
        "ease_of_use": row.ease_of_use,
        "comment": row.comment,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def summary(db: Session, user: User, lab: Lab) -> dict:
    quiz = load_quiz(lab.slug)
    cert_pathway = certification_quiz.public_pathway_for_lab(lab)
    completed = (
        db.query(LabCompletion.id)
        .filter(
            LabCompletion.user_id == user.id,
            LabCompletion.lab_id == lab.id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        )
        .first()
        is not None
    )
    if not quiz and not cert_pathway:
        return {
            "available": False,
            "lab": {"slug": lab.slug, "name": lab.name},
            "completed": completed,
            "optional": True,
        }
    attempts = (
        db.query(ExerciseQuizAttempt)
        .filter(
            ExerciseQuizAttempt.user_id == user.id,
            ExerciseQuizAttempt.lab_id == lab.id,
            ExerciseQuizAttempt.completed_at.isnot(None),
        )
        .order_by(ExerciseQuizAttempt.id.desc())
        .all()
    )
    best = max((row.score or 0 for row in attempts), default=None)
    feedback = (
        db.query(ExerciseQuizFeedback)
        .filter(
            ExerciseQuizFeedback.user_id == user.id,
            ExerciseQuizFeedback.lab_id == lab.id,
        )
        .first()
    )
    if quiz:
        source = quiz["source"]
        certification = quiz["certification"]
        question_count = len(quiz["questions"])
        attempt_count = question_sample_count(quiz)
    elif cert_pathway:
        source = "certification"
        certification = {
            "name": cert_pathway["name"],
            "code": cert_pathway.get("code") or "",
            "url": cert_pathway.get("url") or "",
            "scope": cert_pathway["notice"],
        }
        question_count = cert_pathway["question_count"]
        attempt_count = cert_pathway["sample_size"]
    else:
        source = None
        certification = None
        question_count = 0
        attempt_count = 0
    return {
        "available": True,
        "optional": True,
        "lab": {"slug": lab.slug, "name": lab.name},
        "completed": completed,
        "source": source,
        "certification": certification,
        "pathway": cert_pathway,
        "question_count": question_count,
        "attempt_question_count": attempt_count,
        "passing_score": PASSING_SCORE,
        "attempts": len(attempts),
        "best_score": best,
        "last_attempt": attempts[0].taken_at.isoformat() if attempts and attempts[0].taken_at else None,
        "feedback": _feedback_payload(feedback),
        "benchmark_notice": (
            "This is optional benchmark practice, not an exam item. "
            "Use it to check your understanding and guide the next exercise."
        ),
    }


def start_attempt(db: Session, user: User, lab: Lab) -> dict:
    previous = _previous_keys(db, user.id, lab.id)
    quiz = load_quiz(lab.slug)
    if quiz:
        count = question_sample_count(quiz)
        selected = sample_questions(quiz, previous, count)
        certification_label = quiz["certification"]["code"] or quiz["certification"]["name"]
        source = quiz["source"]
    else:
        cert_selected = certification_quiz.sample_for_lab(
            lab,
            count=certification_quiz.SAMPLE_SIZE,
            previous_keys=previous,
        )
        if not cert_selected:
            raise ValueError("No knowledge check is available for this exercise")
        selected = cert_selected
        pathway = cert_selected[0]["pathway"]
        certification_label = " ".join(
            part for part in (pathway.get("name"), pathway.get("code")) if part
        )
        source = "certification"
    course_id = course_id_for_lab(db, user.id, lab.id)
    attempt = ExerciseQuizAttempt(
        user_id=user.id,
        lab_id=lab.id,
        course_id=course_id,
        certification=certification_label,
        question_keys=json.dumps([
            question.get("key") or question["id"] for question in selected
        ]),
        answers="{}",
        total=len(selected),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return {
        "attempt_id": attempt.id,
        "source": source,
        "question_count": len(selected),
        "passing_score": PASSING_SCORE,
        "questions": [
            {
                "id": question.get("key") or question["id"],
                "prompt": question["prompt"],
                "options": question["options"],
                "difficulty": question["difficulty"],
            }
            for question in selected
        ],
    }


def submit_attempt(
    db: Session,
    user: User,
    lab: Lab,
    attempt_id: int,
    answers: dict,
    feedback: dict | None = None,
) -> dict:
    quiz = load_quiz(lab.slug)
    attempt = (
        db.query(ExerciseQuizAttempt)
        .filter(
            ExerciseQuizAttempt.id == attempt_id,
            ExerciseQuizAttempt.user_id == user.id,
            ExerciseQuizAttempt.lab_id == lab.id,
        )
        .first()
    )
    if not attempt:
        raise ValueError("Attempt not found")
    if attempt.completed_at is not None:
        raise ValueError("This attempt has already been submitted")

    selected_ids = json.loads(attempt.question_keys or "[]")
    by_id = {}
    if quiz:
        by_id.update({question["id"]: question for question in quiz["questions"]})
    for key in selected_ids:
        if key.startswith(certification_quiz.CERT_PREFIX):
            question = certification_quiz.resolve_question(key)
            if question:
                by_id[key] = question
    if not by_id:
        raise ValueError("No knowledge check is available for this exercise")
    quiz_source = (
        "certification"
        if any(key.startswith(certification_quiz.CERT_PREFIX) for key in selected_ids)
        else (quiz.get("source") if quiz else None)
    )
    previous_best = max(_best_scores(db, user.id, lab.id), default=None)
    results = []
    correct_count = 0
    stored_answers = {}
    for question_id in selected_ids:
        question = by_id.get(question_id)
        if not question:
            continue
        selected = answers.get(question_id)
        try:
            selected = int(selected) if selected is not None else None
        except (TypeError, ValueError):
            selected = None
        stored_answers[question_id] = selected
        is_correct = selected == question["correct"]
        if is_correct:
            correct_count += 1
        results.append({
            "id": question["id"],
            "prompt": question["prompt"],
            "options": question["options"],
            "selected": selected,
            "correct_index": question["correct"],
            "correct_option": question["options"][question["correct"]],
            "correct": is_correct,
            "explanation": question["explanation"],
            "reference": question["reference"],
        })

    total = len(results)
    score = round(correct_count / total * 100) if total else 0
    passed = score >= PASSING_SCORE
    attempt.answers = json.dumps(stored_answers)
    attempt.score = score
    attempt.correct = correct_count
    attempt.total = total
    attempt.passed = passed
    attempt.completed_at = datetime.now(timezone.utc)
    db.commit()

    if feedback:
        _record_feedback(db, user, lab, feedback, attempt.course_id)
    check_quiz_achievements(
        db, user.id, lab.id, score, previous_best,
        total=total, quiz_source=quiz_source,
    )
    best = max(_best_scores(db, user.id, lab.id), default=score)
    return {
        "attempt_id": attempt.id,
        "score": score,
        "correct": correct_count,
        "total": total,
        "passed": passed,
        "passing_score": PASSING_SCORE,
        "best_score": best,
        "results": results,
        "benchmark_notice": (
            "Use the explanations and references to close the gap. "
            "You can try another randomised set at any time."
        ),
    }


def record_feedback(db: Session, user: User, lab: Lab, feedback: dict) -> None:
    """Public wrapper for the optional post-quiz experience ratings."""
    _record_feedback(
        db, user, lab, feedback,
        course_id_for_lab(db, user.id, lab.id),
    )


def _record_feedback(
    db: Session,
    user: User,
    lab: Lab,
    feedback: dict,
    course_id: Optional[int],
) -> None:
    row = (
        db.query(ExerciseQuizFeedback)
        .filter(
            ExerciseQuizFeedback.user_id == user.id,
            ExerciseQuizFeedback.lab_id == lab.id,
        )
        .first()
    )
    if row is None:
        row = ExerciseQuizFeedback(
            user_id=user.id,
            lab_id=lab.id,
            course_id=course_id,
        )
        db.add(row)
    for field in ("satisfaction", "relevance", "usefulness", "ease_of_use"):
        value = feedback.get(field)
        if value is not None:
            try:
                value = int(value)
            except (TypeError, ValueError):
                value = None
            if value is not None and 1 <= value <= 5:
                setattr(row, field, value)
    comment = (feedback.get("comment") or "").strip()
    row.comment = comment or None
    row.course_id = course_id or row.course_id
    db.commit()


def list_attempts(db: Session, user: User, lab: Lab) -> dict:
    rows = (
        db.query(ExerciseQuizAttempt)
        .filter(
            ExerciseQuizAttempt.user_id == user.id,
            ExerciseQuizAttempt.lab_id == lab.id,
            ExerciseQuizAttempt.completed_at.isnot(None),
        )
        .order_by(ExerciseQuizAttempt.id.desc())
        .all()
    )
    return {
        "best_score": max((row.score or 0 for row in rows), default=None),
        "attempts": [
            {
                "id": row.id,
                "score": row.score,
                "correct": row.correct,
                "total": row.total,
                "passed": row.passed,
                "taken_at": row.taken_at.isoformat() if row.taken_at else None,
            }
            for row in rows
        ],
    }


def course_quiz_metrics(db: Session, course_id: int) -> dict:
    """Aggregate quiz participation and post-quiz experience ratings."""
    attempts = (
        db.query(ExerciseQuizAttempt)
        .filter(ExerciseQuizAttempt.course_id == course_id)
        .all()
    )
    feedback_rows = (
        db.query(ExerciseQuizFeedback)
        .filter(ExerciseQuizFeedback.course_id == course_id)
        .all()
    )
    best: dict[tuple[int, int], int] = {}
    for row in attempts:
        key = (row.user_id, row.lab_id)
        best[key] = max(best.get(key, 0), row.score or 0)
    respondents = {row.user_id for row in attempts} | {row.user_id for row in feedback_rows}
    labs = {row.lab_id for row in attempts}

    def average(values):
        clean = [value for value in values if value is not None]
        return round(sum(clean) / len(clean), 2) if clean else None

    return {
        "attempts": len(attempts),
        "respondents": len(respondents),
        "labs": len(labs),
        "accuracy": average(list(best.values())),
        "satisfaction": average([row.satisfaction for row in feedback_rows]),
        "relevance": average([row.relevance for row in feedback_rows]),
        "usefulness": average([row.usefulness for row in feedback_rows]),
        "ease_of_use": average([row.ease_of_use for row in feedback_rows]),
        "feedback_responses": len(feedback_rows),
    }
