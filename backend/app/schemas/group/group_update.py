from typing import Optional

from app.schemas import CamelModel

class GroupUpdate(CamelModel):
    nom_groupe: str
    description: Optional[str] = None
