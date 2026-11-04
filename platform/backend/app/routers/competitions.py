"""Opt-in special competitions.

Competitions are deliberately separate from the learning record: a learner
joins an event explicitly, only solves inside the event window count, and the
event leaderboard is time-boxed. The score reuses the course scoreboard rules
(completion, no-hint, first-attempt, speed, and competition first blood).
"""
from datetime import datetime, timezone
from typing import List, Optional, Literal
import base64
import binascii
import io
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_active_user, get_current_instructor_user
from app.database import get_db
from app.models import (
    Achievement,
    Competition,
    CompetitionLab,
    CompetitionParticipant,
    CompetitionSponsor,
    Lab,
    LabCompletion,
    Level,
    User,
)
from app.routers.courses import calculate_lab_score
from app.services.achievements import (
    COMPETITION_BADGE_INFO,
    award_competition_placements,
    competition_achievement_display,
    competition_achievement_parts,
)

router = APIRouter()

_SPONSOR_LOGO_RE = re.compile(
    r"^data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=\s]+)$"
)
_MAX_SPONSOR_LOGO_BYTES = 256 * 1024


def _validate_logo(value: str, label: str = "Logo") -> str:
    """Accept a small raster image and reject disguised payloads."""
    match = _SPONSOR_LOGO_RE.match(value)
    if not match:
        raise ValueError(f"{label} must be a PNG, JPEG, or WebP image")
    try:
        raw = base64.b64decode(re.sub(r"\s+", "", match.group(2)), validate=True)
    except (binascii.Error, ValueError):
        raise ValueError(f"{label} data is not valid base64")
    if len(raw) > _MAX_SPONSOR_LOGO_BYTES:
        raise ValueError(f"{label} must be 256 KB or smaller")
    try:
        from PIL import Image
        with Image.open(io.BytesIO(raw)) as image:
            width, height = image.size
            if width < 1 or height < 1 or width * height > 1_048_576:
                raise ValueError(f"{label} dimensions are too large")
            declared = "jpeg" if match.group(1).lower() == "jpg" else match.group(1).lower()
            if (image.format or "").lower() != declared:
                raise ValueError(f"{label} content does not match its image type")
            image.verify()
    except ValueError:
        raise
    except Exception:
        raise ValueError(f"{label} is not a readable image")
    return value


def _validate_sponsor_logo(value: str) -> str:
    return _validate_logo(value, "Sponsor logo")


def _validate_competition_logo(value: str) -> str:
    return _validate_logo(value, "Competition logo")



class CompetitionSponsorInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    logo_data: Optional[str] = Field(None, max_length=400_000)
    website_url: Optional[str] = Field(None, max_length=500)
    tier: Literal["gold", "silver", "bronze"] = "gold"

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Sponsor name is required")
        return cleaned

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("website_url")
    @classmethod
    def clean_website(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if not re.match(r"^https?://", cleaned, re.IGNORECASE):
            cleaned = f"https://{cleaned}"
        if len(cleaned) > 500:
            raise ValueError("Sponsor website URL is too long")
        return cleaned

    @field_validator("logo_data")
    @classmethod
    def validate_logo(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        return _validate_sponsor_logo(value)


def _clean_competition_logo(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    return _validate_competition_logo(value)


class CompetitionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    logo_data: Optional[str] = Field(None, max_length=400_000)
    start_at: datetime
    end_at: datetime
    lab_ids: List[int] = Field(..., min_length=1)
    sponsors: List[CompetitionSponsorInput] = Field(default_factory=list)


class CompetitionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    logo_data: Optional[str] = Field(None, max_length=400_000)
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    lab_ids: Optional[List[int]] = Field(None, min_length=1)
    sponsors: Optional[List[CompetitionSponsorInput]] = None
    is_active: Optional[bool] = None


SPONSOR_TIER_ORDER = {"gold": 0, "silver": 1, "bronze": 2}


def _sponsor_payload(row: CompetitionSponsor) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "logo_data": row.logo_data,
        "website_url": row.website_url,
        "tier": row.tier,
    }


def _ordered_sponsors(competition: Competition) -> list:
    return sorted(
        competition.sponsors,
        key=lambda row: (
            SPONSOR_TIER_ORDER.get(row.tier, 9),
            row.sort_order or 0,
            row.id or 0,
        ),
    )


def _replace_sponsors(
    db: Session, competition: Competition, sponsors: List[CompetitionSponsorInput]
):
    db.query(CompetitionSponsor).filter(
        CompetitionSponsor.competition_id == competition.id
    ).delete(synchronize_session=False)
    db.flush()
    for order, sponsor in enumerate(sponsors):
        db.add(CompetitionSponsor(
            competition_id=competition.id,
            name=sponsor.name,
            description=sponsor.description,
            logo_data=sponsor.logo_data,
            website_url=sponsor.website_url,
            tier=sponsor.tier,
            sort_order=order,
        ))


def _aware(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _status(competition: Competition, now: datetime) -> str:
    if getattr(competition, "is_archived", False):
        return "archived"
    if not competition.is_active:
        return "inactive"
    if now < _aware(competition.start_at):
        return "upcoming"
    if now > _aware(competition.end_at):
        return "ended"
    return "active"


def _can_manage(competition: Competition, user: User) -> bool:
    return user.role == "admin" or competition.created_by == user.id


def _competition_or_404(db: Session, competition_id: int) -> Competition:
    competition = db.query(Competition).options(
        joinedload(Competition.sponsors)
    ).filter(
        Competition.id == competition_id
    ).first()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition


def _require_manage(competition: Competition, user: User):
    if not _can_manage(competition, user):
        raise HTTPException(
            status_code=403, detail="Only the organiser or an admin can change this competition"
        )


def _lab_rows(db: Session, competition_id: int):
    return db.query(CompetitionLab).options(
        joinedload(CompetitionLab.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        CompetitionLab.competition_id == competition_id
    ).order_by(CompetitionLab.sort_order, CompetitionLab.id).all()


def _lab_payload(row: CompetitionLab) -> dict:
    lab = row.lab
    level = lab.level if lab and lab.level else None
    track = level.track if level and level.track else None
    # High-school content is one track of lessons, not a numbered level ladder.
    # Grade 12 material is a special lesson inside it. Neither should read as
    # "Level 12" anywhere a student sees it.
    is_high_school = bool(track and track.slug == "high-school")
    special = bool(level and "grade 12" in (level.name or "").lower())
    if is_high_school:
        level_label = None
    elif special:
        level_label = level.name if level else None
    else:
        level_label = f"Level {level.level_number}" if level else None
    return {
        "id": lab.id if lab else None,
        "name": lab.name if lab else "Removed exercise",
        "slug": lab.slug if lab else None,
        "difficulty": lab.difficulty if lab else None,
        "duration_minutes": lab.duration_minutes if lab else None,
        "track_name": track.name if track else "Uncategorized",
        "track_slug": track.slug if track else None,
        "level_name": level.name if level else "Uncategorized",
        "level_number": level.level_number if level else None,
        "level_label": level_label,
        "is_special_lesson": is_high_school or special,
        "sort_order": row.sort_order,
    }


def _summary(
    competition: Competition,
    current_user: User,
    now: datetime,
    participant_count: int,
    lab_count: int,
    joined: bool,
) -> dict:
    return {
        "id": competition.id,
        "name": competition.name,
        "description": competition.description,
        "logo_data": competition.logo_data,
        "start_at": _iso(competition.start_at),
        "end_at": _iso(competition.end_at),
        "status": _status(competition, now),
        "is_active": competition.is_active,
        "is_archived": bool(getattr(competition, "is_archived", False)),
        "participant_count": participant_count,
        "lab_count": lab_count,
        "joined": joined,
        "can_manage": _can_manage(competition, current_user),
        "sponsors": [
            _sponsor_payload(row) for row in _ordered_sponsors(competition)
        ],
    }


def _leaderboard(
    db: Session,
    competition: Competition,
    current_user: User,
) -> dict:
    lab_rows = _lab_rows(db, competition.id)
    labs = [row.lab for row in lab_rows if row.lab and row.lab.is_active]
    is_manager = _can_manage(competition, current_user)
    participants = db.query(CompetitionParticipant).options(
        joinedload(CompetitionParticipant.user)
    ).filter(
        CompetitionParticipant.competition_id == competition.id
    ).all()
    participants = [p for p in participants if p.user and p.user.is_active]
    # Pending accounts are visible to the organiser as new sign-ups, but they
    # do not appear on the public event leaderboard until approved.
    if not is_manager:
        participants = [p for p in participants if p.user.is_approved]

    if not participants or not labs:
        return {
            "entries": [],
            "my_entry": None,
            "badges": [],
            "registration_counts": {
                "total": len(participants),
                "new_user": sum(
                    1 for p in participants if (p.source or "opt_in") == "new_user"
                ),
                "opt_in": sum(
                    1 for p in participants if (p.source or "opt_in") == "opt_in"
                ),
            },
        }

    user_ids = [p.user_id for p in participants]
    lab_ids = [lab.id for lab in labs]
    completions = db.query(LabCompletion).filter(
        LabCompletion.user_id.in_(user_ids),
        LabCompletion.lab_id.in_(lab_ids),
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
        LabCompletion.completed_at >= competition.start_at,
        LabCompletion.completed_at <= competition.end_at,
    ).all()

    completion_map = {
        (row.user_id, row.lab_id): row for row in completions
    }
    first_blood_map = {}
    for row in completions:
        current = first_blood_map.get(row.lab_id)
        if current is None or row.completed_at < current.completed_at:
            first_blood_map[row.lab_id] = row

    entries = []
    for participant in participants:
        score = 0
        solved = 0
        last_solved = None
        for lab in labs:
            completion = completion_map.get((participant.user_id, lab.id))
            if not completion:
                continue
            first = first_blood_map.get(lab.id)
            score += calculate_lab_score(
                completion,
                lab,
                0,
                db,
                first_blood_user_id=first.user_id if first else None,
            )
            solved += 1
            if last_solved is None or completion.completed_at > last_solved:
                last_solved = completion.completed_at

        user = participant.user
        display_name = (
            user.scoreboard_name if getattr(user, "show_on_scoreboard", True)
            else "Anonymous participant"
        )
        anonymous = display_name == "Anonymous participant"
        entries.append({
            "user_id": user.id,
            "username": None if anonymous else user.username,
            "display_name": display_name,
            "score": score,
            "solved_count": solved,
            "last_solved_at": _iso(last_solved),
            "source": participant.source or "opt_in",
            "joined_at": _iso(participant.joined_at),
            "is_me": user.id == current_user.id,
            "_last": last_solved,
            "_joined": participant.joined_at,
        })

    entries.sort(
        key=lambda entry: (
            -entry["score"],
            entry["_last"] is None,
            entry["_last"] or datetime.max,
            entry["_joined"] or datetime.max,
        )
    )
    for rank, entry in enumerate(entries, 1):
        entry["rank"] = rank
        entry.pop("_last", None)
        entry.pop("_joined", None)

    # Event placements are final once the window closes. Awarding here is
    # idempotent and makes the badges visible the first time anyone opens the
    # result, even if the organiser never presses Archive.
    if _status(competition, datetime.now(timezone.utc)) in ("ended", "archived"):
        award_competition_placements(db, competition, entries)
        db.commit()

    achievement_rows = db.query(Achievement).filter(
        Achievement.user_id.in_(user_ids),
        Achievement.achievement_type.like(f"comp_{competition.id}_%"),
    ).all()
    achievements_by_user = {}
    badge_counts = {
        code: {"count": 0, "earners": set()}
        for code in COMPETITION_BADGE_INFO
    }
    for row in achievement_rows:
        parts = competition_achievement_parts(row.achievement_type)
        if not parts or parts[0] != competition.id:
            continue
        display = competition_achievement_display(
            row.achievement_type, competition.name
        )
        if not display:
            continue
        label, icon, description = display
        achievements_by_user.setdefault(row.user_id, []).append({
            "type": row.achievement_type,
            "code": parts[1],
            "label": label,
            "icon": icon,
            "description": description,
        })
        badge_counts[parts[1]]["count"] += 1
        badge_counts[parts[1]]["earners"].add(row.user_id)

    for entry in entries:
        entry["achievements"] = achievements_by_user.get(entry["user_id"], [])

    badges = [
        {
            "code": code,
            "label": info[0],
            "description": info[1],
            "icon": info[2],
            "count": badge_counts[code]["count"],
            "earners": len(badge_counts[code]["earners"]),
        }
        for code, info in COMPETITION_BADGE_INFO.items()
    ]

    registration_counts = {
        "total": len(participants),
        "new_user": sum(1 for p in participants if (p.source or "opt_in") == "new_user"),
        "opt_in": sum(1 for p in participants if (p.source or "opt_in") == "opt_in"),
    }

    # Registration source is organiser information, not public leaderboard data.
    if not is_manager:
        for entry in entries:
            entry.pop("source", None)
            entry.pop("joined_at", None)

    my_entry = next(
        (entry for entry in entries if entry["user_id"] == current_user.id), None
    )
    return {
        "entries": entries,
        "my_entry": my_entry,
        "badges": badges,
        "registration_counts": registration_counts,
    }


@router.get("")
async def list_competitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List competitions. Inactive events are hidden from students."""
    query = db.query(Competition)
    if current_user.role not in ("instructor", "admin"):
        query = query.filter(Competition.is_active == True)
    competitions = query.options(
        joinedload(Competition.sponsors)
    ).order_by(Competition.start_at.desc()).limit(100).all()

    now = datetime.now(timezone.utc)
    competition_ids = [c.id for c in competitions]
    participant_counts = {}
    lab_counts = {}
    joined_ids = set()
    if competition_ids:
        participant_counts = dict(
            db.query(
                CompetitionParticipant.competition_id,
                func.count(CompetitionParticipant.id),
            ).filter(
                CompetitionParticipant.competition_id.in_(competition_ids)
            ).group_by(CompetitionParticipant.competition_id).all()
        )
        lab_counts = dict(
            db.query(
                CompetitionLab.competition_id,
                func.count(CompetitionLab.id),
            ).filter(
                CompetitionLab.competition_id.in_(competition_ids)
            ).group_by(CompetitionLab.competition_id).all()
        )
        joined_ids = {
            row[0] for row in db.query(CompetitionParticipant.competition_id).filter(
                CompetitionParticipant.user_id == current_user.id,
                CompetitionParticipant.competition_id.in_(competition_ids),
            ).all()
        }

    return {
        "competitions": [
            _summary(
                c,
                current_user,
                now,
                participant_counts.get(c.id, 0),
                lab_counts.get(c.id, 0),
                c.id in joined_ids,
            )
            for c in competitions
        ]
    }


@router.get("/public/{competition_id}")
async def public_competition(competition_id: int, db: Session = Depends(get_db)):
    """Minimal public event information for a competition sign-up link."""
    competition = _competition_or_404(db, competition_id)
    if not competition.is_active:
        raise HTTPException(status_code=404, detail="Competition not found")
    now = datetime.now(timezone.utc)
    return {
        "competition": {
            "id": competition.id,
            "name": competition.name,
            "description": competition.description,
            "logo_data": competition.logo_data,
            "start_at": _iso(competition.start_at),
            "end_at": _iso(competition.end_at),
            "status": _status(competition, now),
        }
    }


@router.get("/{competition_id}")
async def get_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = _competition_or_404(db, competition_id)
    if not competition.is_active and current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=404, detail="Competition not found")

    now = datetime.now(timezone.utc)
    lab_rows = _lab_rows(db, competition_id)
    joined = db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition_id,
        CompetitionParticipant.user_id == current_user.id,
    ).first() is not None
    participant_count = db.query(func.count(CompetitionParticipant.id)).filter(
        CompetitionParticipant.competition_id == competition_id
    ).scalar() or 0

    return {
        "competition": _summary(
            competition, current_user, now, participant_count,
            len(lab_rows), joined,
        ),
        "labs": [_lab_payload(row) for row in lab_rows],
        "leaderboard": _leaderboard(db, competition, current_user),
    }


@router.post("", status_code=201)
async def create_competition(
    payload: CompetitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Competition name is required")
    if _aware(payload.end_at) <= _aware(payload.start_at):
        raise HTTPException(status_code=400, detail="End time must be after start time")

    requested_ids = list(dict.fromkeys(payload.lab_ids))
    labs = db.query(Lab).filter(
        Lab.id.in_(requested_ids), Lab.is_active == True
    ).all()
    lab_map = {lab.id: lab for lab in labs}
    missing = [lab_id for lab_id in requested_ids if lab_id not in lab_map]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown or inactive exercise IDs: {missing}",
        )

    competition = Competition(
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
        logo_data=_clean_competition_logo(payload.logo_data),
        start_at=payload.start_at,
        end_at=payload.end_at,
        created_by=current_user.id,
        is_active=True,
    )
    db.add(competition)
    db.flush()
    for order, lab_id in enumerate(requested_ids):
        db.add(CompetitionLab(
            competition_id=competition.id,
            lab_id=lab_id,
            sort_order=order,
        ))
    for order, sponsor in enumerate(payload.sponsors):
        db.add(CompetitionSponsor(
            competition_id=competition.id,
            name=sponsor.name,
            description=sponsor.description,
            logo_data=sponsor.logo_data,
            website_url=sponsor.website_url,
            tier=sponsor.tier,
            sort_order=order,
        ))
    db.commit()
    db.refresh(competition)
    return {"message": "Competition created", "id": competition.id}


@router.patch("/{competition_id}")
async def update_competition(
    competition_id: int,
    payload: CompetitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)

    start_at = payload.start_at if payload.start_at is not None else competition.start_at
    end_at = payload.end_at if payload.end_at is not None else competition.end_at
    if _aware(end_at) <= _aware(start_at):
        raise HTTPException(status_code=400, detail="End time must be after start time")

    if payload.name is not None:
        if not payload.name.strip():
            raise HTTPException(status_code=400, detail="Competition name is required")
        competition.name = payload.name.strip()
    if payload.description is not None:
        competition.description = payload.description.strip() or None
    if payload.logo_data is not None:
        competition.logo_data = _clean_competition_logo(payload.logo_data)
    competition.start_at = start_at
    competition.end_at = end_at
    if payload.is_active is not None:
        competition.is_active = payload.is_active

    if payload.lab_ids is not None:
        requested_ids = list(dict.fromkeys(payload.lab_ids))
        labs = db.query(Lab).filter(
            Lab.id.in_(requested_ids), Lab.is_active == True
        ).all()
        found = {lab.id for lab in labs}
        missing = [lab_id for lab_id in requested_ids if lab_id not in found]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown or inactive exercise IDs: {missing}",
            )
        db.query(CompetitionLab).filter(
            CompetitionLab.competition_id == competition.id
        ).delete()
        for order, lab_id in enumerate(requested_ids):
            db.add(CompetitionLab(
                competition_id=competition.id,
                lab_id=lab_id,
                sort_order=order,
            ))

    if payload.sponsors is not None:
        _replace_sponsors(db, competition, payload.sponsors)

    db.commit()
    return {"message": "Competition updated"}


@router.post("/{competition_id}/archive")
async def archive_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Archive an event: keep every result, hide it from the default list."""
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)
    competition.is_archived = True
    db.commit()
    # Freeze the final placements on the way out, even if the organiser never
    # opened the result after the event window closed.
    _leaderboard(db, competition, current_user)
    return {"message": "Competition archived", "is_archived": True}


@router.post("/{competition_id}/unarchive")
async def unarchive_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)
    competition.is_archived = False
    db.commit()
    return {"message": "Competition restored", "is_archived": False}


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)
    # Event badges are keyed by competition id in achievement_type, so they
    # must be removed with the event; otherwise they would remain in profiles
    # and on the wall with a name that no longer resolves.
    db.query(Achievement).filter(
        Achievement.achievement_type.like(f"comp_{competition.id}_%")
    ).delete(synchronize_session=False)
    db.delete(competition)
    db.commit()
    return {"message": "Competition deleted"}


@router.post("/{competition_id}/join")
async def join_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = _competition_or_404(db, competition_id)
    status = _status(competition, datetime.now(timezone.utc))
    if status in ("ended", "inactive", "archived"):
        raise HTTPException(status_code=400, detail="This competition is closed")
    existing = db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition_id,
        CompetitionParticipant.user_id == current_user.id,
    ).first()
    if not existing:
        db.add(CompetitionParticipant(
            competition_id=competition_id,
            user_id=current_user.id,
            source="opt_in",
        ))
        db.commit()
    return {"message": "Joined competition", "joined": True}


@router.post("/{competition_id}/leave")
async def leave_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = _competition_or_404(db, competition_id)
    db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition.id,
        CompetitionParticipant.user_id == current_user.id,
    ).delete()
    db.commit()
    return {"message": "Left competition", "joined": False}
