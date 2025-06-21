from datetime import datetime
from typing import Optional

from app.core.enum import GiftStatusEnum
from app.schemas import UserDisplaySchema
from .gift_ideas_schema import GiftIdeasSchema
from .gift_response import GiftResponse


class GiftPublicResponse(GiftResponse):
    statut: GiftStatusEnum = GiftStatusEnum.DISPONIBLE
    reserve_par: Optional[UserDisplaySchema] = None
    date_reservation: Optional[datetime] = None
    gift_idea: Optional[GiftIdeasSchema] = None