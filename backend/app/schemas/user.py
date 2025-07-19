from datetime import datetime
from typing import Optional

from app.schemas.base_schema import CamelModel


class UserSchema(CamelModel):
    id: int
    nom: Optional[str]
    prenom: str
    email: str
    google_id: Optional[str]
    password: Optional[str]
    date_creation: datetime

