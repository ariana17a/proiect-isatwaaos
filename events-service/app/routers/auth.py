from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.security import create_access_token, verify_password

router = APIRouter()


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


@router.get("/google/placeholder")
def google_oauth_placeholder():
    return {
        "message": "Google OAuth is not implemented yet.",
        "planned_domain_restriction": settings.google_allowed_domain,
    }
