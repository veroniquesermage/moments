from app.schemas import UserSchema
from app.schemas.gift import GiftBase


class GiftCreate(GiftBase):
    utilisateur: UserSchema
