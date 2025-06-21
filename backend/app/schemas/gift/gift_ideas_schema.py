from app.schemas import CamelModel, UserDisplaySchema


class GiftIdeasSchema(CamelModel):
    id: int
    proposee_par: UserDisplaySchema
    visibilite: bool = False