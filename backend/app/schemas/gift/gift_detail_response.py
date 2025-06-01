from typing import Optional

from app.core.enum import RoleUtilisateur
from app.schemas import CamelModel
from .gift_public_response import GiftPublicResponse
from .gift_shared import GiftSharedSchema
from .gift_delivery_schema import GiftDeliverySchema


class GiftDetailResponse(CamelModel):
    gift: GiftPublicResponse
    delivery: Optional[GiftDeliverySchema]
    partage: Optional[list[GiftSharedSchema]]
    est_partage: bool
    droits_utilisateur: RoleUtilisateur
