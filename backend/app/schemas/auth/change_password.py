from app.schemas import CamelModel


class ChangePassword(CamelModel):
    old_password: str
    new_password: str