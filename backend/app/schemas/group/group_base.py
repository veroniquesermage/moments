from pydantic import ConfigDict

from app.schemas import CamelModel


class GroupBase(CamelModel):
    nom_groupe: str
    description: str
