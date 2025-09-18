from pydantic import BaseModel


class InviteResponse(BaseModel):
    emails_envoyes: list[str]
    emails_invalides: list[str]
    emails_deja_membres: list[str]

    model_config = {"from_attributes": True}