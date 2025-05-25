from typing import Optional

from app.core.enum import RoleUtilisateur
from app.schemas import CamelModel
from app.schemas.gift import GiftResponse
from app.schemas.gift.gift_shared import GiftSharedSchema


class GiftDetailResponse(CamelModel):
    gift: GiftResponse
    partage: Optional[list[GiftSharedSchema]]
    est_partage: bool
    droits_utilisateur: RoleUtilisateur