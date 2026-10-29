"""
Level quiz endpoints: fetch a level's quiz, submit answers, view attempts.
"""
import json as _json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth import get_current_active_user, get_current_admin_user
from app.models import User, Track, Level, LevelQuiz, QuizQuestion, QuizAttempt, Lab, LabCompletion
from app.services.achievements import _award

logger = logging.getLogger(__name__)
router = APIRouter()


def _quiz_for_level(db: Session, level_id: int) -> LevelQuiz | None:
    return db.query(LevelQuiz).options(
        joinedload(LevelQuiz.questions)
    ).filter(LevelQuiz.level_id == level_id, LevelQuiz.is_active == True).first()


def _visible_labs(db, level, user):
    from app.routers.curriculum import get_accessible_exclusive_lab_ids, _is_lab_visible
    accessible = get_accessible_exclusive_lab_ids(db, user.id)
    return [lab for lab in level.labs if _is_lab_visible(lab, user, accessible)]


@router.get("/tracks/{track_slug}/levels/{level_id}/quiz")
async def get_level_quiz(
    track_slug: str,
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    track = db.query(Track).filter(Track.slug == track_slug, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    level = next((lv for lv in track.levels if lv.id == level_id), None)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    quiz = _quiz_for_level(db, level_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="No quiz available for this level")

    # Only allow the quiz once all visible labs are complete.
    visible = _visible_labs(db, level, current_user)
    completed_ids = {r[0] for r in db.query(LabCompletion.lab_id).filter(
        LabCompletion.user_id == current_user.id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()}
    if visible and not all(lab.id in completed_ids for lab in visible):
        raise HTTPException(status_code=403, detail="Complete all exercises in this level before taking the quiz.")

    # Best previous attempt
    best = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz.id,
    ).order_by(QuizAttempt.score.desc()).first()

    questions = []
    for q in quiz.questions:
        options = _json.loads(q.options)
        questions.append({
            "id": q.id,
            "sort_order": q.sort_order,
            "question": q.question,
            "options": options,
        })

    return {
        "quiz_id": quiz.id,
        "title": quiz.title,
        "passing_score": quiz.passing_score,
        "level_id": level.id,
        "level_name": level.name,
        "question_count": len(questions),
        "questions": questions,
        "best_score": best.score if best else None,
        "best_passed": best.passed if best else False,
    }


@router.post("/tracks/{track_slug}/levels/{level_id}/quiz/submit")
async def submit_level_quiz(
    track_slug: str,
    level_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    track = db.query(Track).filter(Track.slug == track_slug, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    level = next((lv for lv in track.levels if lv.id == level_id), None)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    quiz = _quiz_for_level(db, level_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="No quiz available for this level")

    answers = payload.get("answers") or []
    if len(answers) != len(quiz.questions):
        raise HTTPException(status_code=400, detail="Answer count does not match question count")

    correct = 0
    for idx, q in enumerate(quiz.questions):
        selected = answers[idx]
        if selected == q.correct_index:
            correct += 1

    total = len(quiz.questions)
    score = round(correct / total * 100) if total else 0
    passed = score >= quiz.passing_score

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=score,
        total=total,
        correct=correct,
        passed=passed,
        answers=_json.dumps(answers),
        taken_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.commit()

    # Quiz results are recorded in QuizAttempt; a "quiz passed" badge is
    # derived from that record rather than the course-scoped Achievement table
    # (quizzes are attached to levels/tracks, not courses).

    return {
        "score": score,
        "correct": correct,
        "total": total,
        "passed": passed,
        "passing_score": quiz.passing_score,
        "explanations": [
            {"question_id": q.id, "correct_index": q.correct_index, "explanation": q.explanation}
            for q in quiz.questions
        ],
    }


@router.get("/tracks/{track_slug}/levels/{level_id}/quiz/attempts")
async def list_quiz_attempts(
    track_slug: str,
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    track = db.query(Track).filter(Track.slug == track_slug, Track.is_active == True).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    level = next((lv for lv in track.levels if lv.id == level_id), None)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    quiz = _quiz_for_level(db, level_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="No quiz available for this level")

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz.id,
    ).order_by(QuizAttempt.taken_at.desc()).all()

    return {
        "quiz_id": quiz.id,
        "best_score": max((a.score for a in attempts), default=None),
        "attempts": [
            {"id": a.id, "score": a.score, "correct": a.correct, "total": a.total, "passed": a.passed, "taken_at": a.taken_at}
            for a in attempts
        ],
    }