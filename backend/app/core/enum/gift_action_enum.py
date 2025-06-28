from enum import Enum


class GiftActionEnum(str, Enum):
    RESERVER = "RESERVER"
    PRENDRE = "PRENDRE"
    ANNULER_RESERVATION = "ANNULER_RESERVATION"
    RETIRER = "RETIRER"