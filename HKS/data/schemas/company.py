from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: str
    description: Optional[str]
    contacts: Optional[str]
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