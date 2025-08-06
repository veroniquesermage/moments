from app.schemas import CamelModel
from app.schemas.gift import GiftFollowed

class GiftFollowedByAccount(CamelModel):
    account_label: str
    total: float
    gifts: list[GiftFollowed]