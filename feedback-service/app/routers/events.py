from datetime import date as dt_date, datetime, time, timedelta
from pathlib import Path

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user_optional, require_roles

router = APIRouter()
QR_CODES_DIR = Path("/app/data/qrcodes")


def _build_qr_payload(event: models.Event) -> str:
    return event.registration_link or f"{settings.frontend_event_base_url}/{event.id}"


def _build_qr_file_path(event_id: int) -> Path:
    return QR_CODES_DIR / f"event-{event_id}.png"


def _generate_and_store_event_qr(db: Session, event: models.Event) -> None:
    QR_CODES_DIR.mkdir(parents=True, exist_ok=True)

    payload = _build_qr_payload(event)
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    file_path = _build_qr_file_path(event.id)
    image.save(file_path, format="PNG")

    event.qr_code_url = f"/events/{event.id}/qr"
    db.add(event)
    db.commit()
    db.refresh(event)


def _get_event_or_404(db: Session, event_id: int) -> models.Event:
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("organizer", "admin")),
):
    event = models.Event(**event_in.model_dump(), created_by=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)

    _generate_and_store_event_qr(db, event)
    return event


def _filtered_public_events_query(
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    organizer: str | None = Query(default=None),
    date: dt_date | None = Query(default=None),
    participation_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Event).filter(models.Event.is_published.is_(True))

    if category:
        query = query.filter(models.Event.category == category)
    if location:
        query = query.filter(models.Event.location == location)
    if organizer:
        query = query.filter(models.Event.organizer == organizer)
    if participation_type:
        query = query.filter(models.Event.participation_type == participation_type)
    if date:
        day_start = datetime.combine(date, time.min)
        day_end = day_start + timedelta(days=1)
        query = query.filter(models.Event.start_datetime >= day_start)
        query = query.filter(models.Event.start_datetime < day_end)

    return query


@router.get("/", response_model=list[schemas.EventResponse])
def list_public_events(
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    organizer: str | None = Query(default=None),
    date: dt_date | None = Query(default=None),
    participation_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = _filtered_public_events_query(
        category=category,
        location=location,
        organizer=organizer,
        date=date,
        participation_type=participation_type,
        db=db,
    )

    return query.order_by(models.Event.start_datetime.asc()).all()


@router.get("/public", response_model=list[schemas.EventResponse])
def list_public_events_legacy(
    category: str | None = Query(default=None),
    location: str | None = Query(default=None),
    organizer: str | None = Query(default=None),
    date: dt_date | None = Query(default=None),
    participation_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = _filtered_public_events_query(
        category=category,
        location=location,
        organizer=organizer,
        date=date,
        participation_type=participation_type,
        db=db,
    )

    return query.order_by(models.Event.start_datetime.asc()).all()


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user_optional),
):
    event = _get_event_or_404(db, event_id)

    if event.is_published:
        return event

    if not current_user:
        raise HTTPException(status_code=403, detail="Event is not public")
    if current_user.role not in {"admin", "organizer"}:
        raise HTTPException(status_code=403, detail="Event is not public")
    if current_user.role == "organizer" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Event is not public")

    return event


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_in: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("organizer", "admin")),
):
    event = _get_event_or_404(db, event_id)

    if current_user.role == "organizer" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own events")

    for key, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    db.add(event)
    db.commit()
    db.refresh(event)

    if "registration_link" in event_in.model_dump(exclude_unset=True):
        _generate_and_store_event_qr(db, event)

    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("organizer", "admin")),
):
    event = _get_event_or_404(db, event_id)

    if current_user.role == "organizer" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can delete only your own events")

    qr_file_path = _build_qr_file_path(event.id)
    db.delete(event)
    db.commit()

    if qr_file_path.exists():
        qr_file_path.unlink()

    return None


@router.post("/{event_id}/publish", response_model=schemas.EventResponse)
def publish_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("organizer", "admin")),
):
    event = _get_event_or_404(db, event_id)
    if current_user.role == "organizer" and event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can publish only your own events")

    event.is_published = True
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _ics_escape(value: str) -> str:
    """Escape special chars per RFC 5545 §3.3.11."""
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_fold(line: str) -> str:
    """Fold long lines at 75 octets per RFC 5545 §3.1."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    chunks = []
    while len(encoded) > 75:
        chunk = encoded[:75]
        # avoid splitting a UTF-8 multibyte sequence
        while len(chunk) > 0 and (chunk[-1] & 0xC0) == 0x80:
            chunk = chunk[:-1]
        chunks.append(chunk.decode("utf-8"))
        encoded = encoded[len(chunk):]
    chunks.append(encoded.decode("utf-8"))
    return "\r\n ".join(chunks)


def _build_ics(event: models.Event) -> str:
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = event.start_datetime.strftime("%Y%m%dT%H%M%SZ")
    dtend = event.end_datetime.strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//USV Events//MVP//RO",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:event-{event.id}@usv.local",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{_ics_escape(event.title)}",
        f"DESCRIPTION:{_ics_escape(event.description or '')}",
        f"LOCATION:{_ics_escape(event.location)}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ]
    return "\r\n".join(_ics_fold(line) for line in lines)


@router.get("/{event_id}/export-ics", summary="Export event as .ics (Google Calendar)")
def export_event_ics_new(event_id: int, db: Session = Depends(get_db)):
    event = _get_event_or_404(db, event_id)
    if not event.is_published:
        raise HTTPException(status_code=403, detail="Event is not public")

    headers = {"Content-Disposition": f'attachment; filename="event-{event.id}.ics"'}
    return Response(content=_build_ics(event), media_type="text/calendar; charset=utf-8", headers=headers)


@router.get("/{event_id}/export.ics", include_in_schema=False)
def export_event_ics(event_id: int, db: Session = Depends(get_db)):
    """Legacy route kept for backward compatibility."""
    return export_event_ics_new(event_id=event_id, db=db)


@router.get("/{event_id}/qr")
def generate_event_qr(event_id: int, db: Session = Depends(get_db)):
    event = _get_event_or_404(db, event_id)

    qr_file_path = _build_qr_file_path(event.id)
    if not qr_file_path.exists():
        _generate_and_store_event_qr(db, event)

    return FileResponse(path=qr_file_path, media_type="image/png")
