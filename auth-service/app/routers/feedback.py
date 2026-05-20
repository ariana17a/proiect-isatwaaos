from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user, require_roles

router = APIRouter()


def _get_published_event_or_404(db: Session, event_id: int) -> models.Event:
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not event.is_published:
        raise HTTPException(status_code=403, detail="Feedback is allowed only for published events")
    return event


@router.post("/", response_model=schemas.FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = _get_published_event_or_404(db, feedback_in.event_id)

    if event.end_datetime > datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(
            status_code=400,
            detail="Feedback can only be submitted after the event has ended",
        )

    existing = (
        db.query(models.Feedback)
        .filter(
            models.Feedback.event_id == feedback_in.event_id,
            models.Feedback.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You have already submitted feedback for this event")

    feedback = models.Feedback(
        event_id=feedback_in.event_id,
        user_id=current_user.id,
        rating=feedback_in.rating,
        comment=feedback_in.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/event/{event_id}", response_model=list[schemas.FeedbackOut])
def list_feedback_for_event(event_id: int, db: Session = Depends(get_db)):
    _get_published_event_or_404(db, event_id)
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.event_id == event_id)
        .order_by(models.Feedback.created_at.desc())
        .all()
    )


@router.get("/event/{event_id}/stats", response_model=schemas.FeedbackStats)
def get_feedback_stats(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("organizer", "admin")),
):
    event = _get_published_event_or_404(db, event_id)

    if current_user.role == "organizer" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view stats for your own events")

    rows = (
        db.query(models.Feedback.rating, func.count(models.Feedback.id))
        .filter(models.Feedback.event_id == event_id)
        .group_by(models.Feedback.rating)
        .all()
    )

    breakdown: dict[int, int] = {r: 0 for r in range(1, 6)}
    total = 0
    rating_sum = 0
    for rating_val, count in rows:
        breakdown[rating_val] = count
        total += count
        rating_sum += rating_val * count

    average = round(rating_sum / total, 2) if total > 0 else 0.0

    return schemas.FeedbackStats(
        event_id=event_id,
        total_reviews=total,
        average_rating=average,
        rating_breakdown=breakdown,
    )
