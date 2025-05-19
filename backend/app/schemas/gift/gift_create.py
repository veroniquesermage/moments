from app.schemas.gift import GiftBase


class GiftCreate(GiftBase):
    groupeId: int  # fourni par le frontend qui connaît le groupe actif
