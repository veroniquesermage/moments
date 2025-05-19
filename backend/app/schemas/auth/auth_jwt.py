from app.schemas.base_schema import CamelModel
from app.schemas.user import UserSchema

class AuthResponse(CamelModel):
    token: str
    profile: UserSchema
