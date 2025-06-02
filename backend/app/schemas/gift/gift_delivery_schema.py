from datetime import date
from typing import Optional

from app.schemas import CamelModel


class GiftDeliverySchema(CamelModel):
    gift_id: int  # ← simple référence, pas l’objet complet
    prix_reel: Optional[float] = None
    lieu_livraison: Optional[str] = None
    date_livraison: Optional[date] = None
    recu: bool = False
