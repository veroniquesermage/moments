from app.schemas import CamelModel, UserSchema


class GiftIdeasSchema(CamelModel):
    id: int
    cree_par: UserSchema
    visibilite: bool = False