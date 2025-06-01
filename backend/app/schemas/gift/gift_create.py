from typing import Optional

from app.core.enum import GiftStatusEnum
from app.schemas import CamelModel, UserSchema


class GiftCreate(CamelModel):
    destinataire_id: int
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
    statut: GiftStatusEnum = GiftStatusEnum.DISPONIBLE
