"""Standalone certification practice.

The exercise check samples three questions. This service owns the longer drill:
a timed mock exam or a domain drill over the reviewed bank, with answer-key
protection, option shuffling, attempt history, and spaced-repetition selection.

Spaced repetition is deliberately simple and explainable: unseen questions
first, then questions with the highest error rate, then the least recently seen.
No model, no hidden weighting.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import User
from app.models.practice import PracticeSession, PracticeSessionQuestion
from app.services import certification_quiz
from app.services.evidence import _tenant_of

DEFAULT_PASS_MARK = 70
DEFAULT_MOCK_SIZE = 10
MIN_MOCK_SIZE = 3
MAX_MOCK_SIZE = 40
MIN_DURATION_MINUTES = 5

OPTION_LABELS = ("A", "B", "C", "D", "E", "F")


class PracticeError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _pathway(pathway_id: str) -> dict:
    pathway = certification_quiz.pathway_by_id(str(pathway_id))
    if pathway is None:
        raise PracticeError(
            "practice_pathway_unknown",
            "The certification pathway is not in the reviewed bank.",
            404,
        )
    return pathway


def exam_config(pathway: dict) -> dict:
    configured = pathway.get("exam") or {}
    available = len(pathway.get("questions") or [])
    size = int(configured.get("question_count") or min(DEFAULT_MOCK_SIZE, available))
    size = max(MIN_MOCK_SIZE, min(size, MAX_MOCK_SIZE, available))
    duration = int(
        configured.get("duration_minutes") or max(MIN_DURATION_MINUTES, size * 2)
    )
    return {
        "question_count": size,
        "duration_minutes": duration,
        "pass_mark": int(configured.get("pass_mark") or DEFAULT_PASS_MARK),
    }


def pathway_payload(pathway: dict) -> dict:
    questions = list(pathway.get("questions") or [])
    domains = []
    for domain in pathway.get("domains") or []:
        count = sum(1 for question in questions if question.get("domain") == domain.get("id"))
        domains.append(
            {
                "id": domain.get("id"),
                "name": domain.get("name"),
                "weight": domain.get("weight"),
                "question_count": count,
            }
        )
    return {
        **certification_quiz.pathway_summary(pathway),
        "domain_list": domains,
        "exam": exam_config(pathway),
        "notice": (
            "Original practice written to public certification objectives. "
            "Not an exam item and not a certification exam."
        ),
    }


def pathways_payload() -> dict:
    return {
        "pathways": [
            pathway_payload(pathway) for pathway in certification_quiz.pathways()
        ],
        "notice": (
            "Practice is scored locally. A pass here is not a certification."
        ),
    }


def _domain_name(pathway: dict, domain_id: str | None) -> str | None:
    for domain in pathway.get("domains") or []:
        if str(domain.get("id")) == str(domain_id):
            return domain.get("name")
    return None


def _history(db: Session, user: User, pathway_id: str) -> dict[str, dict]:
    rows = (
        db.query(PracticeSessionQuestion.question_id, PracticeSessionQuestion.is_correct,
                 PracticeSession.submitted_at)
        .join(
            PracticeSession,
            PracticeSession.id == PracticeSessionQuestion.session_id,
        )
        .filter(
            PracticeSession.user_id == user.id,
            PracticeSession.pathway_id == pathway_id,
            PracticeSession.status == "submitted",
        )
        .all()
    )
    history: dict[str, dict] = {}
    for question_id, is_correct, submitted_at in rows:
        entry = history.setdefault(
            str(question_id),
            {"seen": 0, "wrong": 0, "last": submitted_at},
        )
        entry["seen"] += 1
        if is_correct is False:
            entry["wrong"] += 1
        if submitted_at and (entry["last"] is None or submitted_at > entry["last"]):
            entry["last"] = submitted_at
    return history


def prioritise(
    pool: list[dict],
    history: dict[str, dict],
    count: int,
) -> list[dict]:
    """Unseen first, then highest error rate, then least recently seen."""
    def key(question: dict):
        entry = history.get(str(question.get("id")))
        if entry is None:
            return (0, 0.0, datetime.min, str(question.get("id")))
        seen = max(int(entry.get("seen") or 0), 1)
        wrong_rate = int(entry.get("wrong") or 0) / seen
        last = entry.get("last") or datetime.min
        return (1, -wrong_rate, last, str(question.get("id")))

    ordered = sorted(pool, key=key)
    selected = ordered[: max(0, int(count))]
    random.SystemRandom().shuffle(selected)
    return selected


def _session_summary(session: PracticeSession, now: datetime | None = None) -> dict:
    current = now or _now()
    remaining = (
        max(int((session.expires_at - current).total_seconds()), 0)
        if session.expires_at
        else None
    )
    return {
        "id": session.id,
        "pathway_id": session.pathway_id,
        "pathway_name": session.pathway_name,
        "mode": session.mode,
        "domain_id": session.domain_id,
        "question_count": session.question_count,
        "duration_minutes": session.duration_minutes,
        "pass_mark": session.pass_mark,
        "status": session.status,
        "started_at": session.started_at.isoformat() + "Z" if session.started_at else None,
        "expires_at": session.expires_at.isoformat() + "Z" if session.expires_at else None,
        "submitted_at": (
            session.submitted_at.isoformat() + "Z" if session.submitted_at else None
        ),
        "score": session.score,
        "total": session.total,
        "percentage": session.percentage,
        "passed": session.passed,
        "timed_out": session.timed_out,
        "remaining_seconds": remaining,
    }


def create_session(
    db: Session,
    user: User,
    payload: dict,
) -> dict:
    pathway = _pathway(payload.get("pathway_id"))
    mode = str(payload.get("mode") or "mock")
    if mode not in {"mock", "domain"}:
        raise PracticeError(
            "practice_mode_invalid",
            "Mode must be mock or domain.",
        )
    questions = list(pathway.get("questions") or [])
    if not questions:
        raise PracticeError(
            "practice_bank_empty",
            "This pathway has no reviewed questions yet.",
        )
    domain_id = None
    pool = questions
    if mode == "domain":
        domain_id = str(payload.get("domain_id") or "").strip()
        if not domain_id:
            raise PracticeError(
                "practice_domain_required",
                "Choose a domain for a domain drill.",
            )
        pool = [q for q in questions if str(q.get("domain")) == domain_id]
        if not pool:
            raise PracticeError(
                "practice_domain_unknown",
                "The domain is not in this pathway.",
                404,
            )
    config = exam_config(pathway)
    requested = int(payload.get("question_count") or config["question_count"])
    count = max(1, min(requested, len(pool), MAX_MOCK_SIZE))
    duration = int(payload.get("duration_minutes") or config["duration_minutes"])
    duration = max(MIN_DURATION_MINUTES, min(duration, 240))
    pass_mark = int(payload.get("pass_mark") or config["pass_mark"])
    pass_mark = max(1, min(pass_mark, 100))

    selected = prioritise(pool, _history(db, user, pathway["id"]), count)
    started = _now()
    session = PracticeSession(
        institution_id=_tenant_of(user),
        user_id=user.id,
        pathway_id=pathway["id"],
        pathway_name=pathway["name"],
        mode=mode,
        domain_id=domain_id,
        question_count=len(selected),
        duration_minutes=duration,
        pass_mark=pass_mark,
        status="active",
        started_at=started,
        expires_at=started + timedelta(minutes=duration),
    )
    db.add(session)
    db.flush()
    for position, question in enumerate(selected, start=1):
        order = list(range(len(question.get("options") or [])))
        random.SystemRandom().shuffle(order)
        db.add(
            PracticeSessionQuestion(
                session_id=session.id,
                position=position,
                question_id=str(question["id"]),
                domain_id=str(question.get("domain") or "") or None,
                option_order=order,
            )
        )
    db.commit()
    db.refresh(session)
    return session_payload(db, user, session.id)


def _owned(db: Session, user: User, session_id: int) -> PracticeSession:
    session = db.get(PracticeSession, session_id)
    if session is None or session.user_id != user.id:
        raise PracticeError(
            "practice_session_not_found",
            "Practice session not found.",
            404,
        )
    return session


def _question_by_id() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for pathway in certification_quiz.pathways():
        for question in pathway.get("questions") or []:
            index[str(question["id"])] = {**question, "pathway": pathway}
    return index


def _presented_options(question: dict, order: list[int]) -> list[str]:
    options = list(question.get("options") or [])
    return [str(options[index]) for index in order if 0 <= index < len(options)]


def session_payload(db: Session, user: User, session_id: int) -> dict:
    session = _owned(db, user, session_id)
    question_index = _question_by_id()
    pathway = _pathway(session.pathway_id)
    questions = []
    for row in session.questions:
        question = question_index.get(str(row.question_id))
        if question is None:
            continue
        order = list(row.option_order or [])
        item = {
            "position": row.position,
            "question_id": row.question_id,
            "domain_id": row.domain_id,
            "domain_name": _domain_name(pathway, row.domain_id),
            "objective": question.get("objective"),
            "difficulty": question.get("difficulty"),
            "style": question.get("style"),
            "prompt": question.get("prompt"),
            "options": _presented_options(question, order),
            "labels": list(OPTION_LABELS[: len(order)]),
        }
        if session.status != "active":
            correct_presented = (
                order.index(question.get("correct"))
                if question.get("correct") in order
                else None
            )
            selected = row.selected_index
            item.update(
                {
                    "selected_index": selected,
                    "correct_index": correct_presented,
                    "is_correct": row.is_correct,
                    "explanation": question.get("explanation"),
                    "reference": question.get("reference"),
                }
            )
        questions.append(item)
    return {
        "session": _session_summary(session),
        "questions": questions,
        "pathway": {
            "id": pathway["id"],
            "name": pathway["name"],
            "code": pathway.get("code"),
            "url": pathway.get("url"),
        },
    }


def submit_session(
    db: Session,
    user: User,
    session_id: int,
    answers: list[dict],
) -> dict:
    session = _owned(db, user, session_id)
    if session.status != "active":
        raise PracticeError(
            "practice_session_submitted",
            "This practice session is already submitted.",
            409,
        )
    question_index = _question_by_id()
    by_position = {row.position: row for row in session.questions}
    seen_positions: set[int] = set()
    for answer in answers:
        try:
            position = int(answer.get("position"))
            selected = int(answer.get("selected_index"))
        except (TypeError, ValueError):
            raise PracticeError(
                "practice_answer_invalid",
                "Each answer needs a position and a selected option.",
            ) from None
        row = by_position.get(position)
        if row is None:
            raise PracticeError(
                "practice_answer_invalid",
                f"Question position {position} is not in this session.",
            )
        if position in seen_positions:
            raise PracticeError(
                "practice_answer_invalid",
                f"Question position {position} is answered twice.",
            )
        if selected < 0 or selected >= len(row.option_order or []):
            raise PracticeError(
                "practice_answer_invalid",
                f"Selected option is out of range for position {position}.",
            )
        seen_positions.add(position)
        question = question_index.get(str(row.question_id))
        if question is None:
            continue
        original = list(row.option_order or [])[selected]
        row.selected_index = selected
        row.is_correct = original == question.get("correct")
        row.answered_at = _now()

    now = _now()
    correct = sum(1 for row in session.questions if row.is_correct)
    total = len(session.questions)
    session.score = correct
    session.total = total
    session.percentage = round(correct / total * 100, 1) if total else 0.0
    session.passed = session.percentage >= session.pass_mark
    session.timed_out = bool(session.expires_at and now > session.expires_at)
    session.status = "submitted"
    session.submitted_at = now
    db.commit()
    db.refresh(session)
    return session_payload(db, user, session.id)


def history(db: Session, user: User, limit: int = 20) -> dict:
    rows = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == user.id)
        .order_by(PracticeSession.started_at.desc())
        .limit(max(1, min(limit, 100)))
        .all()
    )
    return {"sessions": [_session_summary(row) for row in rows]}


def progress(db: Session, user: User) -> dict:
    sessions = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.user_id == user.id,
            PracticeSession.status == "submitted",
        )
        .all()
    )
    totals: dict[str, dict] = {}
    for session in sessions:
        entry = totals.setdefault(
            session.pathway_id,
            {
                "pathway_id": session.pathway_id,
                "pathway_name": session.pathway_name,
                "attempts": 0,
                "best_percentage": 0.0,
                "last_percentage": None,
                "last_at": None,
            },
        )
        entry["attempts"] += 1
        entry["best_percentage"] = max(
            float(entry["best_percentage"] or 0.0),
            float(session.percentage or 0.0),
        )
        if entry["last_at"] is None or (
            session.submitted_at and session.submitted_at > entry["last_at"]
        ):
            entry["last_at"] = session.submitted_at
            entry["last_percentage"] = session.percentage

    domain_rows = (
        db.query(
            PracticeSession.pathway_id,
            PracticeSessionQuestion.domain_id,
            PracticeSessionQuestion.is_correct,
        )
        .join(
            PracticeSessionQuestion,
            PracticeSessionQuestion.session_id == PracticeSession.id,
        )
        .filter(
            PracticeSession.user_id == user.id,
            PracticeSession.status == "submitted",
        )
        .all()
    )
    domains: dict[tuple[str, str], dict] = {}
    for pathway_id, domain_id, is_correct in domain_rows:
        key = (str(pathway_id), str(domain_id or ""))
        entry = domains.setdefault(
            key,
            {"answered": 0, "correct": 0},
        )
        entry["answered"] += 1
        if is_correct:
            entry["correct"] += 1

    pathway_by_id = {
        pathway["id"]: pathway for pathway in certification_quiz.pathways()
    }
    domain_payload = []
    for (pathway_id, domain_id), counts in sorted(domains.items()):
        pathway = pathway_by_id.get(pathway_id, {})
        answered = counts["answered"]
        domain_payload.append(
            {
                "pathway_id": pathway_id,
                "domain_id": domain_id,
                "domain_name": _domain_name(pathway, domain_id) or "Unmapped",
                "answered": answered,
                "correct": counts["correct"],
                "accuracy": (
                    round(counts["correct"] / answered * 100, 1)
                    if answered
                    else 0.0
                ),
            }
        )
    return {
        "pathways": sorted(
            totals.values(),
            key=lambda item: item["pathway_id"],
        ),
        "domains": domain_payload,
        "notice": "Practice accuracy is a study signal, not a certification result.",
    }
