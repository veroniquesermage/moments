from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models.user import User
from app.schemas import UserSchema
from app.services import UserGroupService

router = APIRouter(prefix="/utilisateurs", tags=["utilisateurs"])

@router.get("/groupe/{groupId}", response_model=list[UserSchema])
async def get_users(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> list[UserSchema]:

    logger.info(f"Récupération des membres du group {groupId}")
    return await UserGroupService.get_users(db, current_user, groupId)
