from typing import Optional

from app.schemas import CamelModel


class GroupBase(CamelModel):
    nom_groupe: str
    description: Optional[str]
