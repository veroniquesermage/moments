from typing import Optional

from app.schemas import CamelModel


class UserTiersRequest(CamelModel):
    nom: Optional[str] = None
    prenom: str
    surnom: str