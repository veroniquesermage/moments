from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.main import get_db
from app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    RegisterRequest,
    CheckUserRequest,
)
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@router.post("/check-user", status_code=200)
async def check_user(
    request: CheckUserRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    return await AuthService.check_user(request, db)

@router.post("/google", status_code=200)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.authenticate_google_user(request, db)


@router.post("/login", status_code=200)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.authenticate_email_user(request, db)


@router.post("/register", status_code=201)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.register_user(request, db)

@router.post("/refresh", status_code=200)
async def refresh_token(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.refresh_access_token(db, request)

@router.post("/logout", status_code=200)
async def logout(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.logout(db, request)

