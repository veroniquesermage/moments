from app.schemas import CamelModel

class ExportManagedAccountRequest(CamelModel):
    user_id: int
    group_id: int