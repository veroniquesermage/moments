from app.schemas import CamelModel, UserSchema


class GiftIdeasSchema(CamelModel):
    id: int
    proposee_par: UserSchema
    visibilite: bool = False