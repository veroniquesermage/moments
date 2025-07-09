from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.dependencies.current_user import get_current_user_from_cookie
from app.main import get_db
from app.models import User
from app.schemas.auth import GoogleAuthRequest
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

@router.post("/google", response_model=None)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.authenticate_google_user(request, db)

@router.post("/refresh",  status_code=200)
async def refresh_token(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    await AuthService.refresh_access_token(db, request, current_user)