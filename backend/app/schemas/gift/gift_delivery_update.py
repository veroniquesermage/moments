from datetime import datetime
from typing import Optional

from app.schemas import CamelModel


class GiftDeliveryUpdate(CamelModel):
    prix_reel: Optional[float] = None
    lieu_livraison: Optional[str] = None
    date_livraison: Optional[datetime] = None
    recu: bool = False