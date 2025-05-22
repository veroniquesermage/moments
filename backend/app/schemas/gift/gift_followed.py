from datetime import datetime
from typing import Optional

from app.schemas import UserSchema
from app.schemas.gift import GiftBase


class GiftFollowed(GiftBase):
    id: int
    utilisateur: UserSchema
    dateReservation: Optional[datetime] = None
    lieuLivraison: Optional[str] = None
    dateLivraison: Optional[datetime] = None
    recu: Optional[bool] = False