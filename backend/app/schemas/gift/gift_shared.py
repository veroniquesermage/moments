from app.schemas import CamelModel, UserSchema


class GiftSharedSchema(CamelModel):
    id: int
    preneur: UserSchema
    cadeau_id: int
    participant: UserSchema
    montant: float
    rembourse: bool