from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.security import create_access_token, verify_password
from app.security import hash_password

router = APIRouter()


def _is_student_domain_allowed(email: str) -> bool:
    domain = settings.student_domain.strip().lower()
    if not domain:
        return True
    return email.lower().endswith(f"@{domain}")


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Public self-registration is intentionally limited to student accounts.
    if user_in.role != "student":
        raise HTTPException(status_code=403, detail="Self registration is allowed only for student role")

    if settings.enforce_student_domain_on_register and not _is_student_domain_allowed(user_in.email):
        raise HTTPException(
            status_code=400,
            detail=f"Student email must use @{settings.student_domain}",
        )

    user = models.User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        subject={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        subject={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.get("/google/placeholder")
def google_oauth_placeholder():
    return {
        "message": "Google OAuth is not implemented yet.",
        "planned_domain_restriction": settings.google_allowed_domain,
    }
