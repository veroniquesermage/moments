from app.schemas import CamelModel

class CompleteProfileRequest(CamelModel):
    given_name: str
    family_name: str
