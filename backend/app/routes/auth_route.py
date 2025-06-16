from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.main import get_db
from app.schemas.auth import AuthResponse, GoogleAuthRequest
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

@router.post("/google", response_model=AuthResponse)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    return await AuthService.authenticate_google_user(request, db)
