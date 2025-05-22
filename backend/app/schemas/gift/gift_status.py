from app.core.enum import GiftStatusEnum
from app.schemas import CamelModel


class GiftStatus(CamelModel):
    status: GiftStatusEnum