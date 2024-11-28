from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class ContactDetails(BaseModel):
    email: Optional[str]
    phone_number: Optional[str]
    web_page: Optional[str]
    linkedin: Optional[str]

class CompanyRegister(BaseModel):
    username: str
    password: str
    company_name: str
    description: str
    address: str
    contacts: Optional[ContactDetails]


class CompanyOut(BaseModel):
    id: UUID
    name: str
    address: str
    description: str
    contacts: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)