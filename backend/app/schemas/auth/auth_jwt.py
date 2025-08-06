

from app.schemas.base_schema import CamelModel
from app.schemas.user import UserSchema


class AuthResponse(CamelModel):
    profile: UserSchema
    is_new_user: bool = False
