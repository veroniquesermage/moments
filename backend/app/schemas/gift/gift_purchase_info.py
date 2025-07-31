from typing import Optional

from app.models import GiftPurchaseInfo
from app.schemas import CamelModel, UserTiersResponse


class GiftPurchaseInfoSchema(CamelModel):

    gift_id: int
    prix_reel: Optional[float] = None
    commentaire: Optional[str] = None
    compte_tiers: Optional[UserTiersResponse] = None

    @classmethod
    def from_model(cls, purchase: GiftPurchaseInfo) -> "GiftPurchaseInfoSchema":
        return cls(
            gift_id=purchase.gift_id,
            prix_reel=purchase.prix_reel,
            commentaire=purchase.commentaire,
            compte_tiers=purchase.compte_tiers
        )