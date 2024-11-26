from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    location: Optional[str]  # Ще съдържа името на града
    description: Optional[str]
    contacts: Optional[str]
    phone: Optional[str]  # Ще съдържа телефонния номер
    email: Optional[str]  # Ще съдържа имейл адреса
    website: Optional[str] 
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
    phone: str
    email: str
    website: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)
