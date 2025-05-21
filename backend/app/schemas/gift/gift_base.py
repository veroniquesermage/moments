from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict

from app.core.enum import GiftStatusEnum
from app.schemas import CamelModel


class GiftBase(CamelModel):
    nom: str
    description: Optional[str] = None
    url: Optional[str] = None
    quantite: int = 1
    prix: Optional[float] = None
    commentaire: Optional[str] = None
    priorite: int
    statut: GiftStatusEnum = GiftStatusEnum.DISPONIBLE  # valeur par défaut
    marque: Optional[str] = None
    magasin: Optional[str] = None
    prixReel: Optional[float] = None
    fraisPort: Optional[float] = None


