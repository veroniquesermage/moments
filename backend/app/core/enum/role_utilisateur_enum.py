from enum import Enum


class RoleUtilisateur(str, Enum):
    CREATEUR = "CREATEUR"
    PRENEUR = "PRENEUR"
    PARTICIPANT = "PARTICIPANT"