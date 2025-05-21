from pydantic import BaseModel
from datetime import datetime

from app.core.enum import RoleEnum


class GroupResume(BaseModel):
    id: int
    nom: str
    description: str
    role: RoleEnum
    dateAjout: datetime
