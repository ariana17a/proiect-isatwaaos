"""Funcții de dependență FastAPI pentru autentificare și autorizare.

Aceste funcții sunt injectate în handlere de rute prin :func:`fastapi.Depends`
pentru a asigura autentificarea bazată pe JWT și controlul accesului
pe baza rolurilor utilizatorilor.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Rezolvă și returnează utilizatorul autentificat pe baza token-ului Bearer.

    Args:
        token: Token-ul JWT extras automat din antetul ``Authorization``.
        db: Sesiunea activă de bază de date, injectată de FastAPI.

    Returns:
        Obiectul :class:`~app.models.User` corespunzător token-ului valid.

    Raises:
        HTTPException: Cu codul 401 dacă token-ul lipsește, este invalid
            sau utilizatorul nu mai există în baza de date.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)
) -> models.User | None:
    """Versiune opțională a :func:`get_current_user` – nu ridică eroare pentru cererile neautentificate.

    Args:
        token: Token-ul JWT, opțional. Dacă lipsește, funcția returnează ``None``.
        db: Sesiunea activă de bază de date, injectată de FastAPI.

    Returns:
        Obiectul :class:`~app.models.User` dacă token-ul este valid,
        sau ``None`` dacă cererea este neautentificată.
    """
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        return None

    return db.query(models.User).filter(models.User.id == user_id).first()


def require_roles(*allowed_roles: str):
    """Fabrică o dependență FastAPI care restricționează accesul la rolurile specificate.

    Se utilizează ca decorator de dependență în rutele protejate::

        @router.get("/doar-admin")
        def doar_admin(user = Depends(require_roles("admin"))):
            ...

    Args:
        *allowed_roles: Unul sau mai multe roluri permise
            (ex. ``"admin"``, ``"organizer"``).

    Returns:
        O funcție de dependență care validează rolul utilizatorului curent.

    Raises:
        HTTPException: Cu codul 403 dacă rolul utilizatorului autentificat
            nu se regăsește în lista *allowed_roles*.
    """
    def role_dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission for this action",
            )
        return current_user

    return role_dependency
