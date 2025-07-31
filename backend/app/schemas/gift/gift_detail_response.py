from typing import Optional

from app.core.enum import RoleUtilisateur
from app.schemas import CamelModel
from .gift_delivery_schema import GiftDeliverySchema
from .gift_ideas_schema import GiftIdeasSchema
from .gift_public_response import GiftPublicResponse
from .gift_purchase_info import GiftPurchaseInfoSchema
from .gift_shared import GiftSharedSchema


class GiftDetailResponse(CamelModel):
    gift: GiftPublicResponse
    delivery: Optional[GiftDeliverySchema]  = None
    partage: Optional[list[GiftSharedSchema]]  = None
    ideas: Optional[GiftIdeasSchema]  = None
    purchase_info: Optional[GiftPurchaseInfoSchema] = None
    est_partage: bool
    droits_utilisateur: RoleUtilisateur
