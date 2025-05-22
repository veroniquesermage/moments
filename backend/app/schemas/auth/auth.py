from pydantic import Field
from app.schemas.base_schema import CamelModel


class GoogleAuthRequest(CamelModel):
    code: str
    code_verifier: str = Field(alias="codeVerifier")

