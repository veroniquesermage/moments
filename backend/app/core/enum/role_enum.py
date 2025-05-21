from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    MEMBRE = "MEMBRE"
    INVITE = "INVITE"