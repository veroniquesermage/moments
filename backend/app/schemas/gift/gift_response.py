from typing import Optional

from app.schemas import CamelModel, UserSchema


class GiftResponse(CamelModel):
    id: int
    destinataire: UserSchema
    nom: str
    description: Optional[str] = None
    marque: Optional[str] = None
    magasin: Optional[str] = None
    url: Optional[str] = None
    quantite: int = 1
    prix: Optional[float] = None
    frais_port: Optional[float] = None
    commentaire: Optional[str] = None
    priorite: int
