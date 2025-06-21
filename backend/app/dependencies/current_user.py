from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.database import get_db
from app.models.user import User
from sqlalchemy.future import select

SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # toujours requis par FastAPI

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="❌ Identité utilisateur invalide ou expirée.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Décoder le JWT signé maison
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))

        if user_id is None:
            raise credentials_exception

    except (JWTError, ValueError):
        raise credentials_exception

    # 2. Charger l'utilisateur depuis la base
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user

async def get_current_group_id(x_group_id: int = Header(...)) -> int:
    if not x_group_id:
        raise HTTPException(status_code=400, detail="Le groupe actif est requis via X-Group-Id.")
    return x_group_id