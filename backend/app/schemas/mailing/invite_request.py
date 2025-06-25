from app.schemas import CamelModel


class InviteRequest(CamelModel):
    emails: list[str]
