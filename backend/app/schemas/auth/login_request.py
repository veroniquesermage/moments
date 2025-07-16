from app.schemas import CamelModel


class LoginRequest(CamelModel):
    email: str
    password: str
    rememberMe: bool