from datetime import datetime
from pydantic import BaseModel


class InvitationResponse(BaseModel):
    id: int
    email: str
    date_envoi: datetime
    envoye_par_nom: str
    statut: str  # "EN_ATTENTE" ou "EXPIREE"

    model_config = {"from_attributes": True}