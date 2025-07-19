from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.dependencies.current_user import get_current_user_from_cookie
from app.main import get_db
from app.models import User
from app.schemas import UserSchema
from app.schemas.auth import GoogleAuthRequest, CompleteProfileRequest, RegisterRequest
from app.schemas.auth.change_password import ChangePassword
from app.schemas.auth.login_request import LoginRequest
from app.schemas.auth.reset_password_payload import ResetPasswordPayload
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

@router.post("/google", status_code=200)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.authenticate_google_user(request, db)

@router.post("/credentials", status_code=200)
async def login_with_credentials(
        request: LoginRequest,
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.login_with_credentials(request, db)

@router.post("/register-credentials", status_code=200)
async def authenticate_with_credentials(
        request: RegisterRequest,
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.authenticate_credentials_user(request, db)

@router.post("/refresh", status_code=200)
async def refresh_token(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    return await AuthService.refresh_access_token(db, request)

@router.post("/logout", status_code=200)
async def logout(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    return await AuthService.logout(db, request)

@router.post("/request-password-reset", status_code=204)
async def check_password(
        mail: str,
        db: AsyncSession = Depends(get_db)
):
    await AuthService.request_password_reset(db, mail)

@router.post("/verify-reset-token", status_code=200)
async def verify_reset_token(token: str,
                             db: AsyncSession = Depends(get_db)) -> str:
    return await AuthService.verify_reset_token(db, token)

@router.patch("/complete-profile", status_code=200)
async def complete_profile(
        request: CompleteProfileRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
) -> UserSchema:
    return await AuthService.complete_profile(db, current_user, request)

@router.patch("/change-password", status_code=200)
async def change_password(
        request: ChangePassword,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    return await AuthService.change_password(db, current_user, request)

@router.patch("/reset-password", status_code=200)
async def reset_password(
        request: ResetPasswordPayload,
        db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.reset_password(db, request)

@router.get("/check-email", status_code=204)
async def check_mail(
        login_request: LoginRequest,
        db: AsyncSession = Depends(get_db)
):
    await AuthService.check_mail(db, login_request)


