"""Utilități pentru hashing de parole și gestionarea token-urilor JWT.

Oferă funcții ajutătoare pentru managementul parolelor cu bcrypt
și pentru crearea/validarea token-urilor JWT semnate cu algoritmul HS256,
utilizate în fluxul de autentificare al aplicației.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifică dacă parola în clar corespunde hash-ului stocat.

    Args:
        plain_password: Parola introdusă de utilizator, în clar.
        hashed_password: Hash-ul bcrypt stocat în baza de date.

    Returns:
        ``True`` dacă parola este corectă, ``False`` în caz contrar.
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Generează și returnează hash-ul bcrypt al parolei primite.

    Args:
        password: Parola în clar care urmează să fie stocată.

    Returns:
        Șirul de caractere reprezentând hash-ul bcrypt.
    """
    return pwd_context.hash(password)


def create_access_token(subject: dict, expires_delta: timedelta | None = None) -> str:
    """Codifică datele utilizatorului într-un JWT semnat.

    Args:
        subject: Dicționar cu datele de inclus în token (trebuie să conțină
            ``sub`` cu id-ul utilizatorului și ``role`` cu rolul acestuia).
        expires_delta: Durata de valabilitate a token-ului. Dacă nu este
            specificat, se folosește valoarea din
            :attr:`~app.config.Settings.access_token_expire_minutes`.

    Returns:
        Token JWT compact, semnat cu cheia secretă configurată.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = {**subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """Decodifică și verifică un JWT, returnând datele (claims) conținute.

    Args:
        token: Șirul JWT primit în antetul ``Authorization: Bearer``.

    Returns:
        Dicționar cu datele din token (``sub``, ``role``, ``exp`` etc.).

    Raises:
        ValueError: Dacă token-ul este invalid, alterat sau expirat.
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
