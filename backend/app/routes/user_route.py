from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user_from_cookie, get_current_group_id, \
    get_current_user_from_cookie_with_tiers
from app.models.user import User
from app.schemas import UserSchema, UserDisplaySchema
from app.schemas.user_tiers_request import UserTiersRequest
from app.schemas.user_tiers_response import UserTiersResponse
from app.services import UserGroupService
from app.services.auth.user_service import UserService

router = APIRouter(prefix="/api/utilisateurs", tags=["utilisateurs"])

@router.get("/me", response_model=UserSchema)
async def get_user_in_group(
        current_user: User = Depends(get_current_user_from_cookie) ) -> UserSchema:

    user: UserSchema = UserSchema.from_user(current_user)
    return user


@router.get("/en-commun", response_model=list[UserSchema])
async def get_users_with_shared_groups(
        current_user: User = Depends(get_current_user_from_cookie),
        db: AsyncSession = Depends(get_db) ) -> list[UserSchema]:
    logger.info(f"Récupération de tous les utilisateurs qui partagent un groupe avec l'utilisateur {current_user.id}")
    return await UserService.get_users_with_shared_groups(db, current_user)

@router.get("/me/comptes-tiers", response_model=list[UserTiersResponse])
async def get_managed_account(current_user: User = Depends(get_current_user_from_cookie),
                              group_id: int = Depends(get_current_group_id),
                              db: AsyncSession = Depends(get_db)) -> list[UserTiersResponse]:
    logger.info(f"Récupération des compte-tiers pour l'utilisateur {current_user.id}")

    return await UserService.get_managed_account(current_user, group_id, db)

@router.post("/compte-tiers", response_model=UserTiersResponse, status_code=201)
async def create_managed_account(
        request: UserTiersRequest,
        current_user: User = get_current_user_from_cookie_with_tiers(),
        group_id: int = Depends(get_current_group_id),
        db: AsyncSession = Depends(get_db)) -> UserTiersResponse:

    logger.info(f"Création d'un compte-tiers pour l'utilisateur {current_user.id} - nouveau compte: {request.prenom} {request.nom}")

    return await UserService.create_managed_account(request, current_user, group_id, db)

@router.get("/groupe/{groupId}", response_model=list[UserDisplaySchema])
async def get_users(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> list[UserDisplaySchema]:

    logger.info(f"Récupération des membres du group {groupId}")
    return await UserGroupService.get_users_except_current_user(db, current_user, groupId)
