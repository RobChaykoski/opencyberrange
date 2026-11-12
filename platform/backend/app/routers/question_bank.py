"""Admin-only certification question-bank endpoints.

Learners never receive the full bank: the exercise quiz engine sends only the
sampled prompts and options, and reveals answers and references after submit.
These endpoints are the only place the complete question data, answers, and
references are returned.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user
from app.database import get_db
from app.models import User
from app.services import certification_quiz

router = APIRouter()


@router.get("/question-banks", summary="List certification question banks")
async def list_question_banks(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Return bank summaries and validation counts. Admin only."""
    validation = certification_quiz.validate_banks()
    return {
        "version": certification_quiz.load_banks().get("version"),
        "reviewed_at": certification_quiz.load_banks().get("reviewed_at"),
        "pathways": [
            certification_quiz.pathway_summary(pathway)
            for pathway in certification_quiz.pathways()
        ],
        "validation": {
            "ok": validation["ok"],
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "questions": validation["questions"],
            "pathways": validation["pathways"],
            "reviewed_at": validation["reviewed_at"],
        },
    }


@router.get(
    "/question-banks/{pathway_id}",
    summary="Read one certification question bank",
)
async def get_question_bank(
    pathway_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Return the full bank, including answers, explanations, and references."""
    pathway = certification_quiz.pathway_by_id(pathway_id)
    if pathway is None:
        raise HTTPException(status_code=404, detail="Question bank not found")
    return {
        **certification_quiz.pathway_summary(pathway),
        "questions": pathway.get("questions", []),
        "validation": certification_quiz.validate_banks(),
    }


@router.post("/question-banks/validate", summary="Validate the question banks")
async def validate_question_banks(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Run the static reliability checks and return every issue."""
    return certification_quiz.validate_banks()
