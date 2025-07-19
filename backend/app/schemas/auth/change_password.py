from app.schemas import CamelModel


class ChangePassword(CamelModel):
    email: str
    old_password: str
    new_password: str