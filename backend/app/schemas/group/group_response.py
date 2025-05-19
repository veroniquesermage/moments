from .group_base import GroupBase

class GroupResponse(GroupBase):
    id: int
    code: str

    class Config:
        orm_mode = True
