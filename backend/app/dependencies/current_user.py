from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db
from app.schemas import UserSchema

SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # toujours requis par FastAPI

async def get_current_user_from_cookie(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> UserSchema:

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="❌ Token manquant (cookie)")

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None or payload.get("purpose") != 'access_token':
            raise HTTPException(status_code=401, detail="❌ Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="❌ Token corrompu ou expiré")

    # Récupérer l'utilisateur depuis la DB
    from app.services.auth.user_service import UserService
    user = await UserService.get_user_by_id(db, int(user_id))
    return UserSchema.from_user(user)

async def get_current_group_id(x_group_id: int = Header(...)) -> int:
    if not x_group_id:
        raise HTTPException(status_code=400, detail="Le groupe actif est requis via X-Group-Id.")
    return x_group_id