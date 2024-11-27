from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContactsResponse(BaseModel):
    email: str
    phone_number: str

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: str
    description: Optional[str]
    contacts: Optional[ContactsResponse]  # Nested model
    is_approved: bool
    username: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
class ContactDetails(BaseModel):
    email: Optional[str]
    phone_number: Optional[str]
    web_page: Optional[str]
    linkedin: Optional[str]

