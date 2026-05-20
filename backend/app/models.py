"""Modele ORM SQLAlchemy pentru platforma University Events.

Definește cele trei entități principale din baza de date:
``User`` (utilizator), ``Event`` (eveniment) și ``Feedback`` (recenzie),
împreună cu relațiile dintre ele.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Reprezintă un utilizator înregistrat în platformă.

    Attributes:
        id: Cheia primară auto-incrementată.
        email: Adresa de e-mail unică, folosită la autentificare.
        password_hash: Parola stocată ca hash bcrypt.
        role: Rolul utilizatorului – ``student``, ``organizer`` sau ``admin``.
        created_at: Timestamp UTC la momentul creării contului.
        events: Lista evenimentelor create de acest utilizator
            (disponibilă doar pentru rolurile ``organizer`` și ``admin``).
        feedback_entries: Lista recenziilor trimise de acest utilizator.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="creator")
    feedback_entries: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user")


class Event(Base):
    """Reprezintă un eveniment universitar publicat pe platformă.

    Attributes:
        id: Cheia primară auto-incrementată.
        title: Titlul scurt al evenimentului.
        description: Descriere lungă opțională.
        start_datetime: Data și ora de început (UTC).
        end_datetime: Data și ora de sfârșit (UTC).
        location: Locația fizică sau virtuală a evenimentului.
        category: Categoria tematică (ex. workshop, conferință, seminar).
        participation_type: Modul de participare – ``onsite``, ``online``
            sau ``hybrid``.
        organizer: Numele entității organizatoare.
        registration_link: URL extern de înregistrare (opțional).
        qr_code_url: URL relativ către imaginea QR Code generată automat.
        is_published: Dacă evenimentul este vizibil pentru studenți.
        created_by: Cheia externă către utilizatorul care a creat evenimentul.
        creator: Relație ORM înapoi către :class:`User` creator.
        feedback_entries: Toate recenziile :class:`Feedback` ale acestui eveniment.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    participation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    organizer: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    registration_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    qr_code_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator: Mapped["User"] = relationship("User", back_populates="events")
    feedback_entries: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="event", cascade="all, delete-orphan"
    )


class Feedback(Base):
    """Reprezintă o recenzie trimisă de un student pentru un eveniment finalizat.

    Constrângeri importante:
    - Se permite o singură recenzie per pereche (utilizator, eveniment).
    - Recenzia poate fi trimisă doar după ce evenimentul s-a încheiat.

    Attributes:
        id: Cheia primară auto-incrementată.
        event_id: Cheia externă către evenimentul evaluat :class:`Event`.
        user_id: Cheia externă către utilizatorul care a trimis recenzia :class:`User`.
        rating: Scor întreg în intervalul 1–5.
        comment: Comentariu text liber, opțional.
        created_at: Timestamp UTC la momentul trimiterii recenziei.
        event: Relație ORM înapoi către evenimentul evaluat :class:`Event`.
        user: Relație ORM înapoi către utilizatorul care a trimis recenzia :class:`User`.
    """

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="feedback_entries")
    user: Mapped["User"] = relationship("User", back_populates="feedback_entries")
