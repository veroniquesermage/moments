from app.schemas import CamelModel


class ResetPasswordPayload(CamelModel):
    token: str
    new_password: str
