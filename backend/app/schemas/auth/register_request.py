from typing import Optional

from app.schemas import CamelModel


class RegisterRequest(CamelModel):
    token: str
    prenom: str
    nom: Optional[str]