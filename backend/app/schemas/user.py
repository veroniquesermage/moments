from datetime import datetime

from app.schemas.base_schema import CamelModel


class UserSchema(CamelModel):
    id: int
    nom: str
    prenom: str
    email: str
    google_id: str | None = None
    date_creation: datetime

