from typing import Optional

from app.schemas import CamelModel


class UserDisplaySchema(CamelModel):
    id: int
    nom: str
    prenom: str
    surnom: Optional[str] = None