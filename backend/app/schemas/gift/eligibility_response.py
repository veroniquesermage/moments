from app.schemas import CamelModel


class EligibilityResponse(CamelModel):
    ok: bool
    message: str