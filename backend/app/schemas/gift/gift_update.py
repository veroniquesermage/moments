from datetime import datetime
from typing import Optional

from .gift_create import GiftCreate


class GiftUpdate(GiftCreate):
    id: int
    date_reservation: Optional[datetime] = None