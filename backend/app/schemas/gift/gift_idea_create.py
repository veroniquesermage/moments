from app.schemas import CamelModel
from app.schemas.gift import GiftCreate


class GiftIdeaCreate(CamelModel):
    gift: GiftCreate
    visibilite: bool