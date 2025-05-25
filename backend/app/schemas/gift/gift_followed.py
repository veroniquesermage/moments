from typing import Optional

from app.schemas import CamelModel
from app.schemas.gift import GiftSharedSchema, GiftResponse


class GiftFollowed(CamelModel):
    gift: GiftResponse
    partage: Optional[GiftSharedSchema] = None