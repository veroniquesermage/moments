from enum import Enum

class GiftStatusEnum(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    RESERVE = "RESERVE"
    PRIS = "PRIS"
    PARTAGE = "PARTAGE"
