
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.group import GroupResponse, GroupCreate
from app.services.group_service import GroupService

router = APIRouter(prefix="/groupe", tags=["groupe"])


@router.post("/", response_model=GroupResponse)
async def create_group(
        group: GroupCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await GroupService.create_group(group, current_user, db)


@router.get("/", response_model=list[GroupResponse])
async def get_groups(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await GroupService.get_groups(current_user, db)


@router.post("/rejoindre/{code}", response_model=GroupResponse)
async def get_groups(
        code: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    return await GroupService.join_group(current_user, db, code)
