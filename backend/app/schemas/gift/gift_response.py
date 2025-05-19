from datetime import date
from typing import Optional

from app.schemas.gift import GiftBase


class GiftResponse(GiftBase):
    id: int
    utilisateur_id: int
    groupe_id: int
    reserve_par_id: Optional[int] = None
    dateReservation: Optional[date] = None
    lieuLivraison: Optional[str] = None
    dateLivraison: Optional[date] = None
    recu: Optional[bool] = False

    class Config:
        orm_mode = True
