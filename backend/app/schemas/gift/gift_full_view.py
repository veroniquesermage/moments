from typing import Optional, List

from app.core.enum import RoleUtilisateur
from app.schemas import CamelModel
from .gift_shared import GiftSharedSchema
from .gift_delivery_schema import GiftDeliverySchema
from .gift_response import GiftResponse
from .gift_ideas_schema import GiftIdeasSchema

class GiftFullView(CamelModel):

    gift: GiftResponse
    delivery: Optional[GiftDeliverySchema] = None
    partage: Optional[List[GiftSharedSchema]] = None
    idea: Optional[GiftIdeasSchema] = None
    est_partage: bool
    droits_utilisateur: RoleUtilisateur