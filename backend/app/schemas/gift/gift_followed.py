from typing import Optional

from app.schemas import CamelModel
from . import GiftDeliverySchema
from .gift_public_response import GiftPublicResponse
from .gift_purchase_info import GiftPurchaseInfoSchema
from .gift_shared import GiftSharedSchema


class GiftFollowed(CamelModel):
    gift: GiftPublicResponse
    delivery: Optional[GiftDeliverySchema] = None
    partage: Optional[GiftSharedSchema] = None
    purchase_info: Optional[GiftPurchaseInfoSchema] = None
    est_partage: bool = False