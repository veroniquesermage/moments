from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.main import get_db
from app.schemas.auth import AuthResponse, GoogleAuthRequest
from app.services.auth import auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

@router.post("/google", response_model=AuthResponse)
async def authenticate_with_google(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.authenticate_google_user(request, db)
