from fastapi import APIRouter

from app.schemas.auth import (SignupRequest, LoginRequest, TokenResponse, MessageResponse, RefreshTokenRequest)
from app.services.auth import AuthService


router = APIRouter()
auth_service = AuthService()


@router.post("/signup", response_model=TokenResponse)
async def signup(
    data: SignupRequest,
):
    return await auth_service.signup(data)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest
):
   return await auth_service.login(data)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    data: RefreshTokenRequest,
):
    return await auth_service.refresh_access_token(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshTokenRequest,
):
    return await auth_service.logout(data.refresh_token)
