from pydantic import Field
from app.schemas.base_schema import CamelModel


class GoogleAuthRequest(CamelModel):
    code: str
    code_verifier: str = Field(alias="codeVerifier")
    remember_me: bool


class LoginRequest(CamelModel):
    email: str
    password: str
    remember_me: bool


class RegisterRequest(CamelModel):
    prenom: str
    nom: str
    email: str | None = None
    password: str | None = None
    google_id: str | None = Field(default=None, alias="googleId")
    remember_me: bool


class CheckUserRequest(CamelModel):
    email: str
    is_google_login: bool = Field(alias="isGoogleLogin")


