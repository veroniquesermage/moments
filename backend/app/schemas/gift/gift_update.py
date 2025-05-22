from typing import Optional
from datetime import datetime

from app.schemas.gift import GiftBase


class GiftUpdate(GiftBase):
    id: int
    dateReservation: Optional[datetime] = None
    lieuLivraison: Optional[str] = None
    dateLivraison: Optional[datetime] = None
    recu: Optional[bool] = False

