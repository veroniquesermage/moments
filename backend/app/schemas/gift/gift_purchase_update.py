from typing import Optional

from app.schemas import CamelModel, UserTiersResponse


class GiftPurchaseUpdate(CamelModel):

    gift_id: int
    prix_reel: Optional[float] = None
    commentaire: Optional[str] = None
    compte_tiers: Optional[UserTiersResponse] = None