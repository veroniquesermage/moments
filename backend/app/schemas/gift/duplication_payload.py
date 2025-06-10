from app.schemas import CamelModel


class DuplicationPayload(CamelModel):
    new_dest_id: int