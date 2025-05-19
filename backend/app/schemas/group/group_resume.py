from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    MEMBRE = "MEMBRE"
    INVITE = "INVITE"

class GroupResume(BaseModel):
    id: int
    nom: str
    description: str
    role: RoleEnum
    dateAjout: datetime

    class Config:
        orm_mode = True
