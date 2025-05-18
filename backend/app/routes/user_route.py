from fastapi import Depends
from app.dependencies.current_user import get_current_user
from app.models.user import User
from app.router import router


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return current_user
