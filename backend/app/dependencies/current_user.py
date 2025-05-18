from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.database import get_db
from app.models.user import User
from sqlalchemy.future import select

SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(lambda: None)) -> User:
    from fastapi.security import OAuth2PasswordBearer

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # On n'utilise pas tokenUrl ici, mais c'est requis par la classe
    token = await oauth2_scheme()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identité utilisateur invalide ou expirée.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception

    return user
