from pydantic import BaseModel
from typing import Optional, Any


class InvitationValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    invitation: Optional[Any] = None  # Will be Invitation model
    group: Optional[Any] = None       # Will be Group model

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}
