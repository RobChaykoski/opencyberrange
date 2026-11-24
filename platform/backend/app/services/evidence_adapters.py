"""Adapters that turn deterministic learner activity into evidence.

Flags and knowledge checks are verified by the platform, so they are recorded
as automatically accepted evidence. The adapters use the reviewed competency
contract for the lab and the versioned ``automatic-check`` rubric. A missing
contract or rubric is a no-op: evidence is never invented from a partial model.

The public functions used by request handlers run in a background task with
their own database session, so a failure here cannot break a correct flag or a
submitted quiz.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ExerciseQuizAttempt, Lab, LabCompletion, User
from app.services.competency_contract import contract_for_lab
from app.services.evidence import auto_accept_record, create_record

logger = logging.getLogger(__name__)

AUTO_RUBRIC = "automatic-check"
AUTO_RUBRIC_VERSION = "1.0"
ADAPTER_VERSION = "1.0"
AUTO_CRITERION = "verified"


def _competency_links(contract: dict | None) -> list[dict]:
    if not contract:
        return []
    links = []
    for item in contract.get("competency_ids") or []:
        if not isinstance(item, dict):
            continue
        competency_id = str(item.get("id") or "").strip()
        if not competency_id:
            continue
        try:
            weight = float(item.get("weight") or 1.0)
        except (TypeError, ValueError):
            weight = 1.0
        links.append(
            {
                "competency_id": competency_id,
                "criteria": [AUTO_CRITERION],
                "weight": weight,
            }
        )
    return links


def record_flag_evidence(
    db: Session,
    learner: User,
    lab: Lab,
    completion: LabCompletion | None = None,
) -> object | None:
    """Record one accepted flag-evidence record for a lab completion."""

    contract = contract_for_lab(lab.slug)
    links = _competency_links(contract)
    if not links:
        logger.info("No competency contract for flag evidence: %s", lab.slug)
        return None
    record, created = create_record(
        db,
        learner_id=learner.id,
        source_type="flag",
        source_id=lab.slug,
        competencies=links,
        rubric_id=AUTO_RUBRIC,
        rubric_version=AUTO_RUBRIC_VERSION,
        confidence="high",
        confidence_reason="The platform verified the submitted flag.",
        collected_at=getattr(completion, "completed_at", None),
        provenance="flag-adapter",
        provenance_version=ADAPTER_VERSION,
        visibility="both",
        formula_version=(
            getattr(completion, "competency_model_version", None)
            or "competency-v1"
        ),
    )
    if created:
        auto_accept_record(
            db,
            record,
            note="Automatically verified by the flag adapter.",
        )
    return record


def record_quiz_evidence(
    db: Session,
    learner: User,
    lab: Lab,
    attempt: ExerciseQuizAttempt,
) -> object | None:
    """Record accepted evidence for a passed knowledge check."""

    if not attempt.passed:
        return None
    contract = contract_for_lab(lab.slug)
    links = _competency_links(contract)
    if not links:
        logger.info("No competency contract for quiz evidence: %s", lab.slug)
        return None
    score = int(attempt.score or 0)
    confidence = "high" if score >= 90 else "medium"
    record, created = create_record(
        db,
        learner_id=learner.id,
        source_type="quiz",
        source_id=f"{lab.slug}:quiz",
        competencies=links,
        rubric_id=AUTO_RUBRIC,
        rubric_version=AUTO_RUBRIC_VERSION,
        confidence=confidence,
        confidence_reason=(
            f"Knowledge check score {score}% "
            f"({attempt.correct or 0}/{attempt.total or 0})."
        ),
        collected_at=getattr(attempt, "completed_at", None),
        provenance="quiz-adapter",
        provenance_version=ADAPTER_VERSION,
        visibility="both",
        formula_version="competency-v1",
    )
    if created:
        auto_accept_record(
            db,
            record,
            note=f"Automatically verified by the quiz adapter at {score}%.",
        )
    return record


def record_flag_evidence_for_completion(
    learner_id: int,
    lab_id: int,
    completion_id: int,
) -> None:
    """Background-task entry point for a flag completion."""

    db = SessionLocal()
    try:
        learner = db.query(User).filter(User.id == learner_id).first()
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        completion = (
            db.query(LabCompletion)
            .filter(
                LabCompletion.id == completion_id,
                LabCompletion.user_id == learner_id,
                LabCompletion.lab_id == lab_id,
            )
            .first()
        )
        if learner and lab and completion:
            record_flag_evidence(db, learner, lab, completion)
    except Exception as exc:  # pragma: no cover - defensive background guard
        logger.warning(
            "Flag evidence adapter failed for user %s lab %s: %s",
            learner_id,
            lab_id,
            exc,
        )
        db.rollback()
    finally:
        db.close()


def record_quiz_evidence_for_attempt(
    learner_id: int,
    lab_id: int,
    attempt_id: int,
) -> None:
    """Background-task entry point for a submitted knowledge check."""

    db = SessionLocal()
    try:
        learner = db.query(User).filter(User.id == learner_id).first()
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        attempt = (
            db.query(ExerciseQuizAttempt)
            .filter(
                ExerciseQuizAttempt.id == attempt_id,
                ExerciseQuizAttempt.user_id == learner_id,
                ExerciseQuizAttempt.lab_id == lab_id,
            )
            .first()
        )
        if learner and lab and attempt:
            record_quiz_evidence(db, learner, lab, attempt)
    except Exception as exc:  # pragma: no cover - defensive background guard
        logger.warning(
            "Quiz evidence adapter failed for user %s lab %s: %s",
            learner_id,
            lab_id,
            exc,
        )
        db.rollback()
    finally:
        db.close()
