from datetime import datetime
from typing import Optional

from app.core.enum import GiftStatusEnum
from app.schemas import UserSchema
from .gift_response import GiftResponse
from .gift_ideas_schema import GiftIdeasSchema


class GiftPublicResponse(GiftResponse):
    statut: GiftStatusEnum = GiftStatusEnum.DISPONIBLE
    reserve_par: Optional[UserSchema] = None
    date_reservation: Optional[datetime] = None
    gift_idea: Optional[GiftIdeasSchema] = None