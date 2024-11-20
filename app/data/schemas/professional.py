from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class ProfessionalResponse(BaseModel):
    first_name: str
    last_name: str
    address: str
    status: Optional[str]
    summary: Optional[str]
    is_approved: bool

    model_config = ConfigDict(from_attributes=True)

class ProfessionalOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    address: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)
