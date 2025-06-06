from app.schemas import CamelModel
from app.schemas.gift.gift_public_response import GiftPublicResponse
from app.schemas.gift.gift_ideas_schema import GiftIdeasSchema


class GiftIdeasResponse (CamelModel):

    gift: GiftPublicResponse
    gift_idea: GiftIdeasSchema