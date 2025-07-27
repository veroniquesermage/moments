from typing import Optional

from app.schemas import CamelModel


class UserDisplaySchema(CamelModel):
    id: int
    nom: Optional[str] = None
    prenom: str
    surnom: Optional[str] = None
    role: Optional[str] = None
    is_compte_tiers: bool = False