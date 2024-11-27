from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: str
    description: Optional[str]
    contacts: Optional[UUID]  # Assuming you use UUID for contacts
    is_approved: bool
    username: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CompanyOut(BaseModel):
    id: UUID
    name: str
    address: str
    description: str
    contacts: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)