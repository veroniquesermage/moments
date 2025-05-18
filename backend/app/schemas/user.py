from app.schemas.base_schema import CamelModel


class UserSchema(CamelModel):
    id: int
    name: str
    email: str
    google_id: str

    class Config:
        from_attributes = True
