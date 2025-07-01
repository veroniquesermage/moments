from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models.user import User
from app.schemas import UserSchema, UserDisplaySchema
from app.services import UserGroupService

router = APIRouter(prefix="/api/utilisateurs", tags=["utilisateurs"])

@router.get("/me/", response_model=UserSchema)
async def get_user_in_group(
        current_user: User = Depends(get_current_user) ) -> UserSchema:

    user: UserSchema = UserSchema.model_validate(current_user)
    return user

@router.get("/groupe/{groupId}/", response_model=list[UserDisplaySchema])
async def get_users(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> list[UserDisplaySchema]:

    logger.info(f"Récupération des membres du group {groupId}")
    return await UserGroupService.get_users_except_current_user(db, current_user, groupId)
