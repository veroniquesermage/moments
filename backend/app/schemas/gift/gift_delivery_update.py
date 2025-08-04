from datetime import datetime
from typing import Optional

from app.schemas import CamelModel


class GiftDeliveryUpdate(CamelModel):
    lieu_livraison: Optional[str] = None
    date_livraison: Optional[datetime] = None
    recu: bool = False