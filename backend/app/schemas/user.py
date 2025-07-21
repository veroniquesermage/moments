from datetime import datetime
from typing import Optional

from pydantic import Field, ConfigDict

from app.models import User
from app.schemas.base_schema import CamelModel


class UserSchema(CamelModel):
    id: int
    email: Optional[str] = None
    prenom: str
    nom: Optional[str]
    date_creation: datetime
    is_compte_tiers: bool
    has_password: bool = Field(alias="hasPassword")

    @classmethod
    def from_user(cls, user: User) -> "UserSchema":
        return cls(
            id=user.id,
            prenom=user.prenom,
            nom=user.nom,
            is_compte_tiers=user.is_compte_tiers,
            has_password=bool(user.password)
        )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )