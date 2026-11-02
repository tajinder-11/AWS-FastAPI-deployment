from datetime import datetime, timedelta, timezone
import hashlib
import uuid

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        password,
        hashed_password,
    )


def hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode()
    ).hexdigest()


def create_access_token(
    user_id: str,
) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": user_id,
        "type": "access",
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    user_id: str,
) -> tuple[str, str, datetime]:

    jti = str(uuid.uuid4())

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, jti, expire