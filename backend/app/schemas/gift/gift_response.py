from typing import Optional

from app.schemas import CamelModel, UserDisplaySchema


class GiftResponse(CamelModel):
    id: int
    destinataire: UserDisplaySchema
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
