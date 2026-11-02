from fastapi import HTTPException
import jwt

from app.core.config import settings

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)

from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
)


class AuthService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.refresh_token_repository = RefreshTokenRepository()

    async def create_tokens(
        self,
        user_id: str,
    ):
        await self.refresh_token_repository.revoke_all_for_user(
            user_id
        )   
        access_token = create_access_token(user_id)
        refresh_token, jti, expires_at = create_refresh_token(user_id)
        token_hash = hash_token(refresh_token)

        await self.refresh_token_repository.create(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def signup(
        self,
        data: SignupRequest,
    ):
        email = data.email.lower()

        existing_user = await self.user_repository.get_by_email(
            email
        )

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists",
            )

        password_hash = hash_password(data.password)

        user_data = {
            "name": data.name,
            "email": email,
            "password_hash": password_hash,
        }

        user = await self.user_repository.create(user_data)

        user_id = str(user["_id"])

        return await self.create_tokens(user_id)

    async def login(
        self,
        data: LoginRequest,
    ):
        email = data.email.lower()

        user = await self.user_repository.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        password_valid = verify_password(
            data.password,
            user["password_hash"],
        )

        if not password_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        user_id = str(user["_id"])

        return await self.create_tokens(user_id)

    async def refresh_access_token(
        self,
        refresh_token: str,
    ):
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[
                    settings.JWT_ALGORITHM
                ],
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Refresh token has expired",
            )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token payload",
            )

        session = await self.refresh_token_repository.get_by_jti(jti)

        if not session:
            raise HTTPException(
                status_code=401,
                detail="Refresh session not found",
            )

        if session["revoked"]:
            raise HTTPException(
                status_code=401,
                detail="Refresh token has been revoked",
            )

        token_hash = hash_token(refresh_token)

        if session["token_hash"] != token_hash:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        # Rotate refresh token
        await self.refresh_token_repository.revoke(jti)

        return await self.create_tokens(user_id)
    
    async def logout(self, refresh_token: str,):

        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[
                    settings.JWT_ALGORITHM
                ],
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Refresh token has expired",
            )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
            )

        jti = payload.get("jti")

        if not jti:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        session = await self.refresh_token_repository.get_by_jti(
            jti
        )

        if not session:
            return {
                "message": "Logged out successfully"
            }

        await self.refresh_token_repository.revoke(
            jti
        )

        return {
            "message": "Logged out successfully"
        }