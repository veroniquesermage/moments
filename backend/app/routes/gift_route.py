from bdb import effective
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.gift import GiftResponse
from app.services import GiftService

router = APIRouter(prefix="/cadeaux", tags=["cadeaux"])

@router.get("/", response_model=list[GiftResponse])
async def get_gifts(
        userId: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user) ):

    effective_user_id = userId or current_user.id
    logger.info(f"L'utilisateur concerné est {effective_user_id}")
    return await GiftService.get_gifts(db, effective_user_id)
