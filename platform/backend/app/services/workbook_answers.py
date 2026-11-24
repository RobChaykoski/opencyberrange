"""Learner workbook answers and their evidence records.

The live answer is editable. Each distinct version is snapshotted into the
append-only evidence ledger so an instructor reviews exactly what was submitted.
"""

from __future__ import annotations

import hashlib
import re

from sqlalchemy.orm import Session

from app.models import Lab, User, WorkbookAnswer
from app.services.competency_contract import contract_for_lab
from app.services.evidence import create_record
from app.services.evidence_adapters import competency_links

PROMPT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
ANALYST_RUBRIC = "analyst-answer"
ANALYST_RUBRIC_VERSION = "1.0"
ANALYST_CRITERIA = ["accuracy", "evidence", "analysis", "communication"]
MIN_ANSWER_LENGTH = 10
MAX_ANSWER_LENGTH = 20000


def answer_payload(row: WorkbookAnswer) -> dict:
    return {
        "id": row.id,
        "lab_id": row.lab_id,
        "prompt_key": row.prompt_key,
        "answer_text": row.answer_text,
        "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        "updated_at": row.updated_at.isoformat() + "Z" if row.updated_at else None,
    }


def list_answers(
    db: Session, learner: User, *, lab_id: int | None = None
) -> list[WorkbookAnswer]:
    query = db.query(WorkbookAnswer).filter(WorkbookAnswer.user_id == learner.id)
    if lab_id is not None:
        query = query.filter(WorkbookAnswer.lab_id == lab_id)
    return query.order_by(WorkbookAnswer.updated_at.desc(), WorkbookAnswer.id.desc()).all()


def get_answer(
    db: Session, learner: User, lab_id: int, prompt_key: str = "reflection"
) -> WorkbookAnswer | None:
    return (
        db.query(WorkbookAnswer)
        .filter(
            WorkbookAnswer.user_id == learner.id,
            WorkbookAnswer.lab_id == lab_id,
            WorkbookAnswer.prompt_key == prompt_key,
        )
        .first()
    )


def save_answer(
    db: Session,
    learner: User,
    lab: Lab,
    *,
    prompt_key: str = "reflection",
    answer_text: str,
) -> dict:
    prompt_key = (prompt_key or "reflection").strip().lower()
    if not PROMPT_PATTERN.match(prompt_key):
        raise ValueError("prompt_key must use lowercase letters, numbers, hyphens, or underscores")
    answer_text = (answer_text or "").strip()
    if len(answer_text) < MIN_ANSWER_LENGTH:
        raise ValueError("Answer must be at least 10 characters")
    if len(answer_text) > MAX_ANSWER_LENGTH:
        raise ValueError("Answer must be 20,000 characters or fewer")

    row = get_answer(db, learner, lab.id, prompt_key)
    if row is None:
        row = WorkbookAnswer(
            institution_id=getattr(learner, "institution_id", None) or "default",
            user_id=learner.id,
            lab_id=lab.id,
            prompt_key=prompt_key,
            answer_text=answer_text,
        )
        db.add(row)
    else:
        row.answer_text = answer_text
    db.commit()
    db.refresh(row)

    contract = contract_for_lab(lab.slug)
    links = competency_links(contract, ANALYST_CRITERIA)
    evidence = None
    created = False
    if links:
        answer_hash = hashlib.sha256(answer_text.encode("utf-8")).hexdigest()[:12]
        evidence, created = create_record(
            db,
            learner_id=learner.id,
            source_type="workbook",
            source_id=f"{lab.slug}:{prompt_key}:{answer_hash}",
            competencies=links,
            rubric_id=ANALYST_RUBRIC,
            rubric_version=ANALYST_RUBRIC_VERSION,
            confidence="medium",
            confidence_reason=(
                "Learner-submitted analyst answer; awaiting instructor review."
            ),
            provenance="workbook-adapter",
            provenance_version="1.0",
            visibility="both",
            formula_version="competency-v1",
            content_text=answer_text,
        )
    return {"answer": row, "evidence": evidence, "created": created}
