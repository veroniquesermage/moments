from typing import Optional

from app.core.enum import RoleEnum
from app.schemas import CamelModel, UserSchema
from app.schemas.group import GroupBase, GroupResponse


class GroupDetails(CamelModel):
    groupe: GroupResponse
    admins: list[str]
    surnom: Optional[str] = None
    role: RoleEnum
    prenom: str