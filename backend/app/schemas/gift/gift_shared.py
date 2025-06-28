from app.schemas import CamelModel, UserDisplaySchema


class GiftSharedSchema(CamelModel):
    id: int
    preneur: UserDisplaySchema
    cadeau_id: int
    participant: UserDisplaySchema
    montant: float
    rembourse: bool